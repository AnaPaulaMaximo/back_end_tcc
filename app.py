import pymysql
from flask import Flask, request, jsonify
from flask_cors import CORS
from config import conn, cursor
import google.generativeai as genai
import os
from dotenv import load_dotenv
from pymysql.err import IntegrityError

load_dotenv()

app = Flask(__name__)
CORS(app)

API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=API_KEY)

@app.route('/')
def index():
    return 'API ON', 200

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    senha = data.get('senha')

    if not email or not senha:
        return jsonify({'error': 'Email e senha são obrigatórios.'}), 400

    cursor.execute('SELECT id_aluno, nome, email FROM usuarios WHERE email = %s AND senha = %s', (email, senha))
    usuario = cursor.fetchone()

    if usuario:
        return jsonify({'message': 'Login realizado com sucesso!', 'user': usuario}), 200
    else:
        return jsonify({'error': 'Email ou senha inválidos.'}), 401

@app.route('/cadastrar_usuario', methods=['POST'])
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
    except IntegrityError:
        return jsonify({'error': 'Email já cadastrado.'}), 400

@app.route('/editar_usuario/<int:id_aluno>', methods=['PUT'])
def editar_usuario(id_aluno):
    data = request.get_json()
    nome = data.get('nome')
    email = data.get('email')
    senha = data.get('senha')
    url_foto = data.get('url_foto')

    if not nome or not email or not senha or not url_foto:
        return jsonify({'error': 'Todos os campos são obrigatórios.'}), 400

    cursor.execute('UPDATE usuarios SET nome=%s, email=%s, senha=%s url_foto WHERE id_aluno=%s', (nome, email, senha, url_foto, id_aluno))
    conn.commit()

    if cursor.rowcount == 0:
        return jsonify({'error': 'Usuário não encontrado.'}), 404

    return jsonify({'message': 'Usuário atualizado com sucesso.'})

@app.route('/excluir_usuario/<int:id_aluno>', methods=['DELETE'])
def excluir_usuario(id_aluno):
    cursor.execute('DELETE FROM usuarios WHERE id_aluno=%s', (id_aluno,))
    conn.commit()

    if cursor.rowcount == 0:
        return jsonify({'error': 'Usuário não encontrado.'}), 404

    return jsonify({'message': 'Usuário excluído com sucesso.'})

@app.route('/usuarios', methods=['GET'])
def listar_usuarios():
    cursor.execute('SELECT id_aluno, nome, email, url_foto FROM usuarios')
    usuarios = cursor.fetchall()
    return jsonify(usuarios)

@app.route('/resumo', methods=['POST'])
def resumo():
    data = request.get_json()

    if not data or 'tema' not in data:
        return jsonify({'error': 'O campo "tema" é obrigatório.'}), 400
    tema = data['tema']
    prompt = f"""
Dado o tema '{tema}', primeiro avalie se ele é estritamente relacionado a filosofia ou sociologia e se não contém conteúdo preconceituoso, sexual, violento ou inadequado de qualquer tipo.

O resumo deve ser focado nos principais tópicos do tema '{tema}'.

Se o tema for inválido (não relacionado a filosofia/sociologia ou contendo termos inadequados), retorne **APENAS** um JSON com a seguinte estrutura e mensagem de erro específica, sem texto adicional:
{{"error_message": "Por favor, escolha um tema relacionado a filosofia ou sociologia, e que não seja preconceituoso, sexual ou inadequado."}}
"""

    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt)
        texto = response.text.strip()
        return jsonify({"assunto": tema, "contedo": texto})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/correcao', methods=['POST'])
def correcao():
    data = request.get_json()

    if not data or 'tema' not in data or 'texto' not in data:
        return jsonify({'error': 'Os campos "tema" e "texto" são obrigatórios.'}), 400

    tema = data['tema']
    texto = data['texto']

    
    prompt = f""""Você é um professor especializado em Filosofia e Sociologia. precisa corrigir o texto que seu aluno mandou sobre o tema '{tema}'. esse é o texto do aluno: '{texto}'.você terá que ver se oque eles escreveram está certo e dar um feedback de forma resumida, não foque na ortografia ou gramática e sim no conteúdo
 Dado o tema '{tema}', primeiro avalie se ele é estritamente relacionado a filosofia ou sociologia e se não contém conteúdo preconceituoso, sexual, violento ou inadequado de qualquer tipo.

Se o tema for inválido (não relacionado a filosofia/sociologia ou contendo termos inadequados), retorne **APENAS** um JSON com a seguinte estrutura e mensagem de erro específica, sem texto adicional:
{{"error_message": "Por favor, escolha um tema relacionado a filosofia ou sociologia, e que não seja preconceituoso, sexual ou inadequado."}}
"""

    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt)
        texto_corrigido = response.text.strip()
        return jsonify({"texto": texto, "contedo": texto_corrigido})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/flashcard', methods=['POST'])
def flashcard():
    data = request.get_json()

    if not data or 'tema' not in data:
        return jsonify({'error': 'O campo "tema" é obrigatório.'}), 400

    tema = data['tema']
    prompt = f"""
Dado o tema '{tema}', primeiro avalie se ele é estritamente relacionado a filosofia ou sociologia e se não contém conteúdo preconceituoso, sexual, violento ou inadequado de qualquer tipo.

Se o tema for válido, Gere 12 perguntas para flashcards sobre o tema '{tema}'. Retorne a pergunta e a resposta correta, a resposta deve ser breve e acertiva. Estrutura: Pergunta: [pergunta] Resposta: [resposta]

Se o tema for inválido (não relacionado a filosofia/sociologia ou contendo termos inadequados), retorne **APENAS** um JSON com a seguinte estrutura e mensagem de erro específica, sem texto adicional:
{{"error_message": "Por favor, escolha um tema relacionado a filosofia ou sociologia, e que não seja preconceituoso, sexual ou inadequado."}}
"""

    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt)
        texto = response.text.strip()
        return jsonify({"assunto": tema, "contedo": texto})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/quiz', methods=['POST'])
def quiz():
    data = request.get_json()

    if not data or 'tema' not in data:
        return jsonify({'error': 'O campo "tema" é obrigatório.'}), 400

    tema = data['tema']
    
    prompt = f"""Dado o tema '{tema}', primeiro avalie se ele é estritamente relacionado a filosofia ou sociologia e se não contém conteúdo preconceituoso, sexual, violento ou inadequado de qualquer tipo.

Se o tema for válido, gere um quiz com 10 questões sobre ele. Retorne as questões **APENAS** em formato JSON, sem qualquer texto adicional, formatação Markdown de blocos de código ou outros caracteres fora do JSON. Cada questão deve ser um objeto com as seguintes chaves:
- "pergunta": (string) O texto da pergunta.
- "opcoes": (array de strings) Um array com 4 opções de resposta.
- "resposta_correta": (string) A letra da opção correta (ex: "a", "b", "c", "d").

Exemplo de formato JSON esperado para um quiz válido:
[
  {{
    "pergunta": "Qual a capital do Brasil?",
    "opcoes": ["Rio de Janeiro", "São Paulo", "Brasília", "Salvador"],
    "resposta_correta": "c"
  }},
  {{
    "pergunta": "Quem descobriu o Brasil?",
    "opcoes": ["Cristóvão Colombo", "Pedro Álvares Cabral", "Vasco da Gama", "Fernão de Magalhães"],
    "resposta_correta": "b"
  }}
]

Se o tema for inválido (não relacionado a filosofia/sociologia ou contendo termos inadequados), retorne **APENAS** um JSON com a seguinte estrutura e mensagem de erro específica, sem texto adicional:
{{"error_message": "Por favor, escolha um tema relacionado a filosofia ou sociologia, e que não seja preconceituoso, sexual ou inadequado."}}
"""

    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt)
        texto = response.text.strip()
        return jsonify({"assunto": tema, "contedo": texto})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
