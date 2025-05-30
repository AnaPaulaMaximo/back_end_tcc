from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai
import os 
from config import *
import google.generativeai as genai
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
load_dotenv()


app = Flask(__name__)
CORS(app)

# Configuração do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

#api key do google
API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=API_KEY)


# ROTA PRINCIPAL DE TESTE
@app.route('/')
def index():

    return 'API ON', 200

# CADASTRAR USUÁRIO
@app.route('/usuarios', methods=['POST'])
def cadastrar_usuario():
    data = request.get_json()
    nome = data.get('nome')
    email = data.get('email')
    senha = data.get('senha')

    if not nome or not email or not senha:
        return jsonify({'error': 'Todos os campos são obrigatórios.'}), 400

    try:
        cursor.execute('INSERT INTO usuarios (nome, email, senha) VALUES (%s, %s, %s)', (nome, email, senha))
        conn.commit()
        return jsonify({'message': 'Usuário cadastrado com sucesso.'}), 201
    except mysql.connector.IntegrityError:
        return jsonify({'error': 'Email já cadastrado.'}), 400
    

# EDITAR USUÁRIO
@app.route('/usuarios/<int:id>', methods=['PUT'])
def editar_usuario(id):
    data = request.get_json()
    nome = data.get('nome')
    email = data.get('email')
    senha = data.get('senha')

    if not nome or not email or not senha:
        return jsonify({'error': 'Todos os campos são obrigatórios.'}), 400

    cursor.execute('UPDATE usuarios SET nome=%s, email=%s, senha=%s WHERE id=%s', (nome, email, senha, id))
    conn.commit()

    if cursor.rowcount == 0: #mostra quantas linhas foram afetadas pelo update
        return jsonify({'error': 'Usuário não encontrado.'}), 404

    return jsonify({'message': 'Usuário atualizado com sucesso.'})

# EXCLUIR USUÁRIO
@app.route('/usuarios/<int:id>', methods=['DELETE'])
def excluir_usuario(id):
    cursor.execute('DELETE FROM usuarios WHERE id=%s', (id,))
    conn.commit()

    if cursor.rowcount == 0:
        return jsonify({'error': 'Usuário não encontrado.'}), 404

    return jsonify({'message': 'Usuário excluído com sucesso.'})

# Listar todos os usuários
@app.route('/usuarios', methods=['GET'])
def listar_usuarios():
    cursor.execute('SELECT id, nome, email FROM usuarios')
    usuarios = cursor.fetchall()
    return jsonify(usuarios)


#REVISÃO 2 (mapa conceitual)
@app.route('/mapa_conceitual', methods=['GET'])
def mapa_conceitual():

    # Recupera o corpo da requisição POST que deve conter o input 
    data = request.get_json()
        
    if not data or 'tema' not in data:
        return jsonify({'error': 'O campo"tema" é obrigatório.'}), 400

    tema = data['tema']
    
    prompt = f"Gere um parágrafo separadamente para os 4 principais tópicos focado no tema '{tema}'."

    try:
        model = genai.GenerativeModel('gemini-2.0-flash')  
        response = model.generate_content(prompt)
        texto = response.text.strip()
        return jsonify({"assunto": tema, "contedo": texto})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    
#REVISÃO 3 (resumo)  
@app.route('/resumo', methods=['GET'])
def resumo():
     # Recupera o corpo da requisição POST que deve conter o input 
    data = request.get_json()
        
    if not data or 'tema' not in data:
        return jsonify({'error': 'O campo"tema" é obrigatório.'}), 400

    tema = data['tema']
    
    
    prompt = f"Faça um resumo de tudo que aconteceu durante a(o) '{tema}'"

    try:
        model = genai.GenerativeModel('gemini-2.0-flash')  
        response = model.generate_content(prompt)
        texto = response.text.strip()
        return jsonify({"assunto": tema, "contedo": texto})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    

#REVISÃO 4 (correção)
@app.route('/correcao', methods=['GET'])
def correcao():

    # Recupera o corpo da requisição POST que deve conter o input 
    data = request.get_json()
        
    if not data or 'tema' not in data or texto not in data:
        return jsonify({'error': 'O campo"texto" e "tema" são obrigatórios.'}), 400

    tema = data['tema']
    texto = data['texto']
    
    prompt = f"Você é um professor e precisa corrigir o texto que seu aluno mandou sobre o tema '{tema}'. esse é o texto do aluno: '{texto}'"

    try:
        model = genai.GenerativeModel('gemini-2.0-flash')  
        response = model.generate_content(prompt)
        texto = response.text.strip()
        return jsonify({"texto": texto, "contedo": texto})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    

#REVISÃO 5 (flashcard)
@app.route('/flashcard', methods=['GET'])
def fashcard():
# Recupera o corpo da requisição POST que deve conter o input 
    data = request.get_json()
        
    if not data or 'tema' not in data:
        return jsonify({'error': 'O campo"tema" é obrigatório.'}), 400

    tema = data['tema']
    
    prompt = f"Gere 12 perguntas para flashcards sobre o tema '{tema}'. retone a pergunta e a resposta correta com uma breve explicação resumida. essa dever ser a estrutura: Pergunta: [pergunta] Resposta: [resposta] Explicação: [explicação]"

    try:
        model = genai.GenerativeModel('gemini-2.0-flash')  
        response = model.generate_content(prompt)
        texto = response.text.strip()
        return jsonify({"assunto": tema, "contedo": texto})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


#REVISÃO 6 (quiz)
@app.route('/quiz', methods=['GET'])
def quiz():
    # Recupera o corpo da requisição POST que deve conter o input 
    data = request.get_json()
        
    if not data or 'tema' not in data:
        return jsonify({'error': 'O campo"tema" é obrigatório.'}), 400

    tema = data['tema']
    
    prompt = f"Gere uma prova com 10 questões sobre o tema '{tema}'. retone a pergunta com 4 alternativas e qual é a resposta correta"

    try:
        model = genai.GenerativeModel('gemini-2.0-flash')  
        response = model.generate_content(prompt)
        texto = response.text.strip()
        return jsonify({"assunto": tema, "contedo": texto})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)