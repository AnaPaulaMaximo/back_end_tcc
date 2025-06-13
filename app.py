from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai
import os
import google.generativeai as genai
from dotenv import load_dotenv
from model import Aluno, db  # <--- IMPORTA db DO model.py
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash
from sqlalchemy import text

load_dotenv()

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)



# ROTA PRINCIPAL DE TESTE
@app.route('/')
def index():

    return 'API ON', 200



# CADASTAR ALUNO
@app.route('/cadastrar_usuarios', methods=['POST'])
def cadastrar_usuario():
    data = request.get_json()
    nome = data.get('nome')
    email = data.get('email')
    senha = data.get('senha')

    if not email or not senha:
        return jsonify({'error': 'Email e senha são obrigatórios.'}), 400

    senha_hash = generate_password_hash(senha)
    aluno = Aluno(nome=nome, email=email, senha_hash=senha_hash)

    try:
        db.session.add(aluno)
        db.session.commit()
        return jsonify({'message': 'Usuário cadastrado com sucesso.'}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Email já cadastrado.'}), 400
    
    

# EDITAR ALUNO
@app.route('/editar_usuarios/<int:id>', methods=['PUT'])
def editar_usuario(id):
    data = request.get_json()
    nome = data.get('nome')
    email = data.get('email')
    senha = data.get('senha')

    if not email or not senha:
        return jsonify({'error': 'Email e senha são obrigatórios.'}), 400

    aluno = Aluno.query.get(id)
    if not aluno:
        return jsonify({'error': 'Usuário não encontrado.'}), 404

    aluno.nome = nome
    aluno.email = email
    aluno.senha_hash = generate_password_hash(senha)
    db.session.commit()

    return jsonify({'message': 'Usuário atualizado com sucesso.'})

# EXCLUIR ALUNO
@app.route('/excluir_usuarios/<int:id>', methods=['DELETE'])
def excluir_usuario(id):
    aluno = Aluno.query.get(id)
    if not aluno:
        return jsonify({'error': 'Usuário não encontrado.'}), 404

    db.session.delete(aluno)
    db.session.commit()
    return jsonify({'message': 'Usuário excluído com sucesso.'})

# LISTAR ALUNOS
@app.route('/usuarios', methods=['GET'])
def listar_usuarios():
    alunos = Aluno.query.all()
    if not alunos:
        return jsonify({'message': 'Nenhum usuário encontrado.'}), 404
    return jsonify([
        {
            'id_aluno': aluno.id_aluno,
            'nome': aluno.nome,
            'email': aluno.email,
            'url_foto': aluno.url_foto
        }
        for aluno in alunos
    ])

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
    with app.app_context():
        try:
            db.session.execute(text('SELECT 1'))
            print('Banco conectado!')
        except Exception as e:
            print(f'status: Erro na conexão - {str(e)}')

    app.run(debug=True)
    #para hostear localmente: , host='0.0.0.0', port=5000