from flask_sqlalchemy import SQLAlchemy
from datetime import date

db = SQLAlchemy()

class Aluno(db.Model):
    __tablename__ = 'aluno'

    id_aluno = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)
    url_foto = db.Column(db.String(255))

    matriculas = db.relationship('Matricula', backref='aluno', cascade="all, delete-orphan")
    progresso = db.relationship('Progresso', backref='aluno', cascade="all, delete-orphan")
    certificados = db.relationship('Certificado', backref='aluno', cascade="all, delete-orphan")
    respostas = db.relationship('RespostaAluno', backref='aluno', cascade="all, delete-orphan")


class Curso(db.Model):
    __tablename__ = 'curso'

    id_curso = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    carga_horaria = db.Column(db.Integer)
    tipo = db.Column(db.String(50), default='regular')

    materias = db.relationship('CursoMateria', back_populates='curso', cascade="all, delete-orphan")
    matriculas = db.relationship('Matricula', backref='curso', cascade="all, delete-orphan")
    progresso = db.relationship('Progresso', backref='curso', cascade="all, delete-orphan")
    certificados = db.relationship('Certificado', backref='curso', cascade="all, delete-orphan")
    questionarios = db.relationship('Questionario', backref='curso', cascade="all, delete-orphan")


class Materia(db.Model):
    __tablename__ = 'materia'

    id_materia = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)

    conteudos = db.relationship('Conteudo', backref='materia', cascade="all, delete-orphan")
    cursos = db.relationship('CursoMateria', back_populates='materia', cascade="all, delete-orphan")


class CursoMateria(db.Model):
    __tablename__ = 'cursomateria'

    id_curso = db.Column(db.Integer, db.ForeignKey('curso.id_curso', ondelete='CASCADE'), primary_key=True)
    id_materia = db.Column(db.Integer, db.ForeignKey('materia.id_materia', ondelete='CASCADE'), primary_key=True)

    curso = db.relationship('Curso', back_populates='materias')
    materia = db.relationship('Materia', back_populates='cursos')


class Conteudo(db.Model):
    __tablename__ = 'conteudo'

    id_conteudo = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(50), nullable=False)
    url_arquivo = db.Column(db.String(255))
    titulo = db.Column(db.String(100))
    id_materia = db.Column(db.Integer, db.ForeignKey('materia.id_materia', ondelete='SET NULL'))


class Matricula(db.Model):
    __tablename__ = 'matricula'

    id_matricula = db.Column(db.Integer, primary_key=True)
    id_aluno = db.Column(db.Integer, db.ForeignKey('aluno.id_aluno', ondelete='CASCADE'))
    id_curso = db.Column(db.Integer, db.ForeignKey('curso.id_curso', ondelete='CASCADE'))
    data_matricula = db.Column(db.Date, default=date.today)


class Progresso(db.Model):
    __tablename__ = 'progresso'

    id_progresso = db.Column(db.Integer, primary_key=True)
    id_aluno = db.Column(db.Integer, db.ForeignKey('aluno.id_aluno', ondelete='CASCADE'))
    id_curso = db.Column(db.Integer, db.ForeignKey('curso.id_curso', ondelete='CASCADE'))
    percentual = db.Column(db.Numeric(5, 2))
    ultima_data = db.Column(db.Date)


class Certificado(db.Model):
    __tablename__ = 'certificado'

    id_certificado = db.Column(db.Integer, primary_key=True)
    id_aluno = db.Column(db.Integer, db.ForeignKey('aluno.id_aluno', ondelete='CASCADE'))
    id_curso = db.Column(db.Integer, db.ForeignKey('curso.id_curso', ondelete='CASCADE'))
    data_emissao = db.Column(db.Date)


class Questionario(db.Model):
    __tablename__ = 'questionario'

    id_questionario = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100))
    id_curso = db.Column(db.Integer, db.ForeignKey('curso.id_curso', ondelete='CASCADE'))

    perguntas = db.relationship('Pergunta', backref='questionario', cascade="all, delete-orphan")


class Pergunta(db.Model):
    __tablename__ = 'pergunta'

    id_pergunta = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.Text, nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    id_questionario = db.Column(db.Integer, db.ForeignKey('questionario.id_questionario', ondelete='CASCADE'))

    alternativas = db.relationship('Alternativa', backref='pergunta', cascade="all, delete-orphan")
    respostas = db.relationship('RespostaAluno', backref='pergunta', cascade="all, delete-orphan")


class Alternativa(db.Model):
    __tablename__ = 'alternativa'

    id_alternativa = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.String(255), nullable=False)
    correta = db.Column(db.Boolean, default=False)
    id_pergunta = db.Column(db.Integer, db.ForeignKey('pergunta.id_pergunta', ondelete='CASCADE'))


class RespostaAluno(db.Model):
    __tablename__ = 'respostaaluno'

    id_resposta = db.Column(db.Integer, primary_key=True)
    id_aluno = db.Column(db.Integer, db.ForeignKey('aluno.id_aluno', ondelete='CASCADE'))
    id_pergunta = db.Column(db.Integer, db.ForeignKey('pergunta.id_pergunta', ondelete='CASCADE'))
    resposta_texto = db.Column(db.Text)
    id_alternativa = db.Column(db.Integer, db.ForeignKey('alternativa.id_alternativa', ondelete='SET NULL'), nullable=True)

    alternativa = db.relationship('Alternativa')
