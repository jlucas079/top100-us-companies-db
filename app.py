import warnings
warnings.filterwarnings('ignore', category=FutureWarning)
from flask import abort, render_template, Flask
import logging
import db

APP = Flask(__name__)

# Start page
@APP.route('/')
def index():
    stats = {}
    stats = db.execute('''
    SELECT * FROM
      (SELECT COUNT(*) n_empresas FROM Empresas)
    JOIN
      (SELECT COUNT(*) n_estados FROM Estados)
    JOIN
      (SELECT COUNT(*) n_setores FROM "Setores Industriais")
    JOIN 
      (SELECT COUNT(*) n_fundadores FROM Fundadores)
    JOIN 
      (SELECT COUNT(*) n_faturacoes FROM Faturacoes)
    ''').fetchone()
    logging.info(stats)
    return render_template('index.html',stats=stats)

# Empresas
@APP.route('/empresas/')
def list_empresas():
    empresas = db.execute(
      '''
      SELECT IDEmpresa, Rank, Nome, NFuncionarios 
      FROM Empresas
      ORDER BY Rank
      ''').fetchall()
    return render_template('movie-list.html', empresas=empresas)


@APP.route('/empresas/<int:id>/')
def get_empresa(id):
  empresa = db.execute(
      '''
      SELECT e.IDEmpresa, e.Nome, e.Rank, e.NFuncionarios 
      FROM Empresas e
      WHERE IDEmpresa = ?
      ''', [id]).fetchone()

  if empresa is None:
     abort(404, 'Empresa id {} does not exist.'.format(id))

  setor = db.execute(
      '''
      SELECT s.IDSetor, s.Nome
      FROM "Setores Industriais" s JOIN Empresas c ON c.IDSetor = s.IDSetor
      WHERE c.IDEmpresa = ?
      ''', [id]).fetchall()

  fundador = db.execute(
      '''
      Select f.IDFundador, f.Nome, f.Idade, f.Nacionalidade
      From Fundadores f JOIN Empresas c ON  f.IDEmpresa = c.IDEmpresa
      where c.IDEmpresa= ?
      ''', [id]).fetchall()

  return render_template('movie.html', 
           empresa=empresa, setor=setor, fundador=fundador)

@APP.route('/empresas/search/<expr>/')
def search_empresa(expr):
  search = { 'expr': expr }
  expr = '%' + expr + '%'
  empresas = db.execute(
      ''' 
      SELECT e.IDEmpresa, e.Nome
      FROM Empresas e
      WHERE e.Nome LIKE ?
      ''', [expr]).fetchall()
  return render_template('movie-search.html',
           search=search,empresas=empresas)

# Fundadores
@APP.route('/fundadores/')
def list_fundadores():
    fundadores = db.execute('''
      SELECT f.IDFundador, f.Nome, f.Idade, f.Nacionalidade
      FROM Fundadores f
      ORDER BY f.Nome
    ''').fetchall()
    return render_template('actor-list.html', fundadores=fundadores)


@APP.route('/fundadores/<int:id>/')
def view_empresas_by_fundadores(id):
  fundador = db.execute(
    '''
    SELECT f.IDFundador, f.Nome, f.Idade, f.Nacionalidade
    FROM Fundadores f
    WHERE f.IDFundador = ?
    ''', [id]).fetchone()

  if fundador is None:
     abort(404, 'Fundador id {} does not exist.'.format(id))

  empresas = db.execute(
    '''
    SELECT e.IDEmpresa, e.Nome
    FROM Empresas e JOIN Fundadores f ON  e.IDEmpresa = f.IDEmpresa
    WHERE IDFundador = ?
    ''', [id]).fetchall()

  return render_template('actor.html', 
           fundador=fundador, empresas=empresas)
 
@APP.route('/fundadores/search/<expr>/')
def search_fundador(expr):
  search = { 'expr': expr }
  # SQL INJECTION POSSIBLE! - avoid this!
  fundadores = db.execute(
      ' SELECT IDFundador, Nome '
      ' FROM Fundadores ' 
      ' WHERE Nome LIKE \'%' + expr + '%\''
    ).fetchall()
  
  return render_template('actor-search.html', 
           search=search,fundadores=fundadores)

# Setor
@APP.route('/setores/')
def list_setores():
    setores = db.execute('''
      SELECT s.Nome, "Lucro setorial(bilioes)" as l
      FROM "Setores Industriais" s
      ORDER BY Nome
    ''').fetchall()
    return render_template('genre-list.html', setores=setores)

@APP.route('/setores/<int:id>/')
def view_empresa_by_setores(id):
  setor = db.execute(
    '''
    SELECT s.IDSetor, s.Nome
    FROM "Setores Industriais" s
    WHERE IDSetor = ?
    ''', [id]).fetchone()

  if setor is None:
     abort(404, 'Setor id {} does not exist.'.format(id))

  empresas = db.execute(
    '''
    SELECT e.IDEmpresa, e.Nome
    FROM Empresas e JOIN "Setores Industriais" f ON e.IDSetor = f.IDSetor
    WHERE f.IDSetor = ?
    ''', [id]).fetchall()

  return render_template('genre.html', 
           setor=setor, empresas=empresas)


