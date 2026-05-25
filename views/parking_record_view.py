from app import app
from db.connect_db import connect_db
from flask import make_response, jsonify, request
from datetime import datetime, timedelta
from utils import login_required


def check_and_release_expired_spots(cursor):
    """
    Função utilitária para liberar automaticamente no banco de dados
    as vagas cujo tempo de ocupação já expirou, garantindo que não 
    afete novas reservas ativas na mesma vaga.
    """
    sql = """
        UPDATE parking_spot pr_spot
        SET pr_spot.is_occupied = 0
        WHERE pr_spot.is_occupied = 1
          AND pr_spot.id NOT IN (
              -- Mantém ocupada se houver algum registro onde o tempo de saída ainda não chegou
              SELECT DISTINCT parking_spot_id
              FROM parking_record
              WHERE exit_time > NOW() 
                AND parking_spot_id IS NOT NULL
          )
    """
    cursor.execute(sql)

@app.route('/parking-records/', methods=['GET'])
@login_required
def get_parking_records():
    try:
        banco = connect_db()
        cursor = banco.cursor()

        # EXECUTA A LIMPEZA AUTOMÁTICA DE VAGAS EXPIRADAS ANTES DE LISTAR
        check_and_release_expired_spots(cursor)
        banco.commit()

        sql = '''SELECT id, parking_spot_id, vehicle_id, entry_time, exit_time, created_at, updated_at 
                 FROM parking_record;'''
        cursor.execute(sql)
        resultado_fetchall = cursor.fetchall()
        banco.close()

        lista_records_json = [
            {
                "id": record[0],
                "parking_spot_id": record[1],
                "vehicle_id": record[2],
                "entry_time": str(record[3]),
                "exit_time": str(record[4]) if record[4] else None,  # Trata o campo nulo caso o veículo ainda esteja na vaga
                "created_at": str(record[5]),
                "updated_at": str(record[6])
            }
            for record in resultado_fetchall
        ]

        lista_records_json_ordenada = sorted(
            lista_records_json,
            key=lambda x: x['id'],
            reverse=True
        )

        return make_response(
            jsonify(
                mensagem='Lista de registros de estacionamento.',
                total=len(lista_records_json_ordenada),
                dados=lista_records_json_ordenada
            ), 200
        )
    except Exception as e:
        return make_response(jsonify(mensagem="Erro interno ao listar registros.", erro=str(e)), 500)


@app.route('/parking-records/<int:id>/', methods=['GET'])
@login_required
def get_parking_record_detail(id):
    try:
        banco = connect_db()
        cursor = banco.cursor()

        # Executa a limpeza automática de vagas expiradas
        check_and_release_expired_spots(cursor)
        banco.commit()

        sql = '''SELECT id, parking_spot_id, vehicle_id, entry_time, exit_time, created_at, updated_at 
                 FROM parking_record WHERE id = %s;'''
        cursor.execute(sql, (id,))
        record = cursor.fetchone()
        banco.close()

        if not record:
            return make_response(jsonify(mensagem="Registro não encontrado."), 404)
        
        record_json = {
            "id": record[0],
            "parking_spot_id": record[1],
            "vehicle_id": record[2],
            "entry_time": str(record[3]),
            "exit_time": str(record[4]) if record[4] else None,
            "created_at": str(record[5]),
            "updated_at": str(record[6])
        }
        return make_response(jsonify(mensagem="Detalhes do registro de estacionamento.", dados=record_json), 200)
    except Exception as e:
        return make_response(jsonify(mensagem="Erro interno ao buscar registro.", erro=str(e)), 500)


@app.route('/parking-records/', methods=['POST'])
@login_required
def create_parking_record():
    try:
        dados_recebidos = request.get_json()
        
        parking_spot_id = dados_recebidos.get("parking_spot_id")
        vehicle_id = dados_recebidos.get("vehicle_id")
        hours_to_occupy = dados_recebidos.get("hours_to_occupy") #Recebe a qtd de horas

        if not parking_spot_id or not vehicle_id:
            return make_response(jsonify(mensagem="As chaves 'parking_spot_id' e 'vehicle_id' são obrigatórias."), 400)

        if hours_to_occupy is None:
            return make_response(jsonify(mensagem="A chave 'hours_to_occupy' (horas de uso) é obrigatória."), 400)
        
        banco = connect_db()
        cursor = banco.cursor()
        sql_check_vehicle_exists = "SELECT id FROM vehicle WHERE id = %s"
        cursor.execute(sql_check_vehicle_exists,(vehicle_id,))
        if not cursor.fetchone():
            banco.close()
            return make_response(jsonify(mensagem=f"O veículo com o ID {vehicle_id} não existe."), 404)

        # 1- garante que as vagas expiradas sejam limpas antes de checar se a vaga está livre
        check_and_release_expired_spots(cursor)

        # 2- Checa se o vehicle já está em alguma vaga ativa  (exit_time no futuro)
        sql_check_vehicle = """
            SELECT parking_spot_id
            FROM parking_record
            WHERE vehicle_id = %s AND exit_time > NOW();
        """
        cursor.execute(sql_check_vehicle, (vehicle_id,))
        vehicle_active_record = cursor.fetchone()
        if vehicle_active_record:
            banco.close()
            return make_response(jsonify(
                mensagem=f"Este vehicle já está ocupando a vaga ID {vehicle_active_record[0]} e não pode ocupar outra simultaneamente."
            ), 400)

        # 3- checa o status atual da vaga requisitada
        sql_check_spot = 'SELECT is_occupied FROM parking_spot WHERE id = %s;'
        cursor.execute(sql_check_spot, (parking_spot_id,))
        spot_status = cursor.fetchone()

        if not spot_status:
            banco.close()
            return make_response(jsonify(mensagem="A vaga informada não existe."), 404)
        
        if bool(spot_status) and spot_status[0] == 1:
            banco.close()
            return make_response(jsonify(mensagem="Esta vaga já está ocupada por outro veículo."), 400)


        #Calculo automático de datas usando o datetime
        now = datetime.now()
        entry_time_calculated = now.strftime('%Y-%m-%d %H:%M:%S')
        exit_time_calculated = (now + timedelta(hours=int(hours_to_occupy))).strftime('%Y-%m-%d %H:%M:%S')
        
        # Insere o registro informando o entry_time atual e o exit_time calculado
        sql = 'INSERT INTO parking_record (parking_spot_id, vehicle_id, entry_time, exit_time) VALUES (%s, %s, %s,%s);'
        cursor.execute(sql, (parking_spot_id, vehicle_id, entry_time_calculated, exit_time_calculated))
            
        id_criado = cursor.lastrowid

        sql_update_spot = 'UPDATE parking_spot SET is_occupied = 1 WHERE id = %s'
        cursor.execute(sql_update_spot, (parking_spot_id,))
        banco.commit()
        
        sql = '''SELECT id, parking_spot_id, vehicle_id, entry_time, exit_time, created_at, updated_at 
                 FROM parking_record WHERE id = %s;'''
        cursor.execute(sql, (id_criado,))
        r = cursor.fetchone()
        banco.close()

        record_json = {
            "id": r[0], #type:ignore
            "parking_spot_id": r[1], #type:ignore
            "vehicle_id": r[2], #type:ignore
            "entry_time": str(r[3]), #type:ignore
            "exit_time": str(r[4]) if r[4] else None, #type:ignore
            "created_at": str(r[5]), #type:ignore
            "updated_at": str(r[6]) #type:ignore
        }
        return make_response(jsonify(mensagem="Registro de entrada criado com sucesso.", dados=record_json), 201)
    except Exception as e:
        return make_response(jsonify(mensagem="Erro interno ao criar registro.", erro=str(e)), 500)


@app.route('/parking-records/<int:id>/', methods=['PUT'])
@login_required
def put_parking_record(id):
    try:
        banco = connect_db()
        cursor = banco.cursor()
        
        sql = 'SELECT parking_spot_id, vehicle_id, exit_time FROM parking_record WHERE id = %s;'
        cursor.execute(sql, (id,))
        record_atual = cursor.fetchone()
        
        if not record_atual:
            banco.close()
            return make_response(jsonify(mensagem='Registro de estacionamento não encontrado para atualização.'), 404)

        vaga_antiga_id = record_atual
        veiculo_atual_id = record_atual

        check_and_release_expired_spots(cursor)
        
        dados_recebidos = request.get_json()
        
        parking_spot_id = dados_recebidos.get('parking_spot_id', record_atual[0])
        vehicle_id = dados_recebidos.get('vehicle_id', record_atual[1])
        exit_time = dados_recebidos.get('exit_time', record_atual[2])

        # validação preventiva de existencia do vehicle(Caso tenha alterado no PUT)
        if vehicle_id != veiculo_atual_id:
            sql_check_vehicle_exists = "SELECT id FROM vehicle WHERE id = %s"
            cursor.execute(sql_check_vehicle_exists, (vehicle_id,))
            if not cursor.fetchone():
                banco.close()
                return make_response(jsonify(mensagem=f"O veículo com o ID {vehicle_id} informado não existe"), 404)
       
        # Checa se o veículo (novo ou atual) está ativo em OUTRO registro
        sql_check_vehicle = """
            SELECT parking_spot_id 
            FROM parking_record 
            WHERE vehicle_id = %s AND exit_time > NOW() AND id != %s;
        """
        cursor.execute(sql_check_vehicle, (vehicle_id, id))
        vehicle_active_record = cursor.fetchone()
        if vehicle_active_record:
            banco.close()
            return make_response(jsonify(
                mensagem=f"Este veículo já está ocupando a vaga ID {vehicle_active_record[0]} em outro registro ativo."
            ), 400)
        
        # Se a vaga foi alterada, checa se a nova vaga está livre
        if parking_spot_id != vaga_antiga_id:
            sql_check_spot = 'SELECT is_occupied FROM parking_spot WHERE id = %s;'
            cursor.execute(sql_check_spot, (parking_spot_id,))
            spot_status = cursor.fetchone()

            if not spot_status:
                banco.close()
                return make_response(jsonify(mensagem="A nova vaga informada não existe."), 404)
            
            if bool(spot_status) and spot_status == 1:
                banco.close()
                return make_response(jsonify(mensagem="A nova vaga informada já está ocupada por outro veículo."), 400)
            
        # executa a atualização no banco
        sql = '''UPDATE parking_record 
                 SET parking_spot_id=%s, vehicle_id=%s, exit_time=%s 
                 WHERE id=%s;'''
        cursor.execute(sql, (parking_spot_id, vehicle_id, exit_time, id))
        
        # Se foi atualizado manualmente um exit_time que o já passou do horário de agora, libera a vaga.
        if exit_time and datetime.strptime(str(exit_time), '%Y-%m-%d %H:%M:%S') <= datetime.now():
            sql_update_spot = 'UPDATE parking_spot SET is_occupied = 0 WHERE id = %s'
            cursor.execute(sql_update_spot, (parking_spot_id,))
        else:
            # Caso mude o id da vaga no meio do processo por algum motivo, garante consitência
            sql_update_spot = 'UPDATE parking_spot SET is_occupied = 1 WHERE id = %s'
            cursor.execute(sql_update_spot, (parking_spot_id,))
        
        banco.commit()

        sql = '''SELECT id, parking_spot_id, vehicle_id, entry_time, exit_time, created_at, updated_at 
                 FROM parking_record WHERE id = %s;'''
        cursor.execute(sql, (id,))
        r = cursor.fetchone()
        banco.close()
        
        record_json = {
            "id": r[0], #type:ignore
            "parking_spot_id": r[1], #type:ignore
            "vehicle_id": r[2], #type:ignore
            "entry_time": str(r[3]), #type:ignore
            "exit_time": str(r[4]) if r[4] else None, #type:ignore
            "created_at": str(r[5]), #type:ignore
            "updated_at": str(r[6]) #type:ignore
        }
        return make_response(jsonify(mensagem="Registro atualizado com sucesso.", dados=record_json), 200)
    except Exception as e:
        return make_response(jsonify(mensagem="Erro interno ao atualizar registro.", erro=str(e)), 500)


@app.route('/parking-records/<int:id>/', methods=['DELETE'])
@login_required
def delete_parking_record(id):
    try:
        banco = connect_db()
        cursor = banco.cursor()
        
        # busca o parking_spot_id antes de deletar o registro para sabermos qual vaga liberar.
        sql = 'SELECT parking_spot_id FROM parking_record WHERE id=%s;'
        cursor.execute(sql, (id,))
        record = cursor.fetchone()
        
        if not record:
            banco.close()
            return make_response(jsonify(mensagem='Registro não encontrado para deletar.'), 404)

        # extrai o id numérico da tupla usando record
        parking_spot_id = record
        
        # deleta o registro
        sql = 'DELETE FROM parking_record WHERE id=%s;'
        cursor.execute(sql, (id,))

        # Alteração(UPDATE): Como o registro foi excluído, resetamos o status da vaga para 0 (Livre)
        sql_update_spot = 'UPDATE parking_spot SET is_occupied = 0 WHERE id = %s'
        cursor.execute(sql_update_spot, (parking_spot_id,))
        
        banco.commit()
        banco.close()

        return make_response(jsonify(mensagem="Registro deletado com sucesso."), 200)
    except Exception as e:
        return make_response(jsonify(mensagem="Erro interno ao deletar registro.", erro=str(e)), 500)
