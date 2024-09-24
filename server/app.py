import psycopg2
from psycopg2 import sql, Error
from flask import Flask, request, jsonify
from psycopg2 import OperationalError
import json
from flask_cors import CORS  

app = Flask(__name__)
CORS(app)

with open('config.json') as config_file:
    config = json.load(config_file)

db_name = config.get('DB_NAME')
db_user = config.get('DB_USER')
db_password = config.get('DB_PASSWORD')
db_host = config.get('DB_HOST')

# Configuração da conexão com o banco de dados
def get_db_connection():
    try:
        conn = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_password,
            host=db_host
        )
        return conn
    except OperationalError as e:
        print(f"Error connecting to the database: {e}")
        return None

# Funções para interagir com o banco de dados
def adicionar_usuario(nome):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO usuario (nome) VALUES (%s)", (nome,)
            )
            conn.commit()
        except Error as e:
            print(f"Error adding user: {e}")
        finally:
            cursor.close()
            conn.close()

def adicionar_medicamento(nome):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO medicamento (nome) VALUES (%s)", (nome,)
            )
            conn.commit()
        except Error as e:
            print(f"Error adding medication: {e}")
        finally:
            cursor.close()
            conn.close()

def adicionar_lembrete(id_usuario, id_medicamento, horario):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO lembrete (id_usuario, id_medicamento, horario) VALUES (%s, %s, %s)",
                (id_usuario, id_medicamento, horario)
            )
            conn.commit()
        except Error as e:
            print(f"Error adding reminder: {e}")
        finally:
            cursor.close()
            conn.close()

def listar_lembretes():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            # Realiza a junção das tabelas
            cursor.execute("""
                SELECT 
                    lembrete.id, 
                    usuario.nome AS nome_usuario, 
                    medicamento.nome AS nome_medicamento, 
                    lembrete.horario 
                FROM 
                    lembrete
                JOIN 
                    usuario ON lembrete.id_usuario = usuario.id
                JOIN 
                    medicamento ON lembrete.id_medicamento = medicamento.id
            """)
            lembretes = cursor.fetchall()

            lembretes_formatados = []
            for lembrete in lembretes:
                lembretes_formatados.append({
                    'id': lembrete[0],
                    'nome_usuario': lembrete[1],  # Nome do usuário
                    'nome_medicamento': lembrete[2],  # Nome do medicamento
                    'horario': lembrete[3].strftime('%H:%M:%S')  # Converte o horário para string
                })
            
            return lembretes_formatados
        except Error as e:
            print(f"Error listing reminders: {e}")
            return []
        finally:
            cursor.close()
            conn.close()
    return []

##########################################POST

@app.route('/adicionar_usuario', methods=['POST'])
def criar_usuario():
    nome = request.form.get('nome')
    if nome:
        adicionar_usuario(nome)
        return 'Usuário adicionado com sucesso!', 201
    else:
        return 'Nome é obrigatório', 400
    
@app.route('/adicionar_medicamento', methods=['POST'])
def criar_medicamento():
    medicamento = request.form.get('medicamento')
    if medicamento:
        adicionar_medicamento(medicamento)
        return 'Medicamento adicionado com sucesso!', 201
    else:
        return 'Medicamento é obrigatório', 400
    
@app.route('/adicionar_lembrete', methods=['POST'])
def criar_lembrete():
    usuario_nome = request.form.get('usuario')
    medicamento_nome = request.form.get('medicamento')
    horario = request.form.get('horario')

    if usuario_nome and medicamento_nome and horario:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                # Buscar ID do usuário
                cursor.execute("SELECT id FROM usuario WHERE nome = %s", (usuario_nome,))
                usuario = cursor.fetchone()

                # Buscar ID do medicamento
                cursor.execute("SELECT id FROM medicamento WHERE nome = %s", (medicamento_nome,))
                medicamento = cursor.fetchone()

                if usuario and medicamento:
                    id_usuario = usuario[0]
                    id_medicamento = medicamento[0]
                    adicionar_lembrete(id_usuario, id_medicamento, horario)
                    return 'Lembrete adicionado com sucesso!', 201
                else:
                    return 'Usuário ou Medicamento não encontrado', 404
            except Error as e:
                print(f"Error creating reminder: {e}")
                return 'Erro ao criar lembrete', 500
            finally:
                cursor.close()
                conn.close()
        else:
            return 'Erro ao conectar ao banco de dados', 500
    else:
        return 'Todos os campos são obrigatórios', 400

####################################### GET
@app.route('/listar_lembretes', methods=['GET'])
def ver_lembretes():
    lembretes = listar_lembretes()
    return jsonify(lembretes), 200

if __name__ == '__main__':
    app.run(debug=True)
