# -*- coding: utf-8 -*-
import urllib.request
import ssl
import textwrap
from bs4 import BeautifulSoup


class ScrapDeMaterias():

    def __init__(self, materias):
        self.materias = materias

    def limpiarTexto(self):
        for br in self.soup.find_all('br'):
            br.replace_with('\n')

    def comenzarScrap(self):
        self.soup = self.crearSoup()
        self.limpiarTexto()
        return self.avisoDeTodasLasMaterias()

    def avisoDeTodasLasMaterias(self):
        avisos = map(lambda materia: self.generarAvisos(
            materia), self.materias)
        separador = '\n' + '╚' + ('═' * 20) + '\n'
        return separador.join(avisos) + separador

    def informacionDeMateria(self, materia):
        seccionDeMateria = self.soup.find('td', text=materia).parent
        return seccionDeMateria.find_all_next('td')

    def diasDeComienzo(self, materia):
        return self.informacionDeMateria(materia)[2].text

    def horarios(self, materia):
        return self.informacionDeMateria(materia)[3].text

    def hayDiasDeComienzo(self, materia):
        return bool(self.diasDeComienzo(materia))

    def hayHorarios(self, materia):
        return bool(self.horarios(materia))

    def tabular(self, texto):
        lineas = texto.strip().split('\n')
        textoWrapeado = '\n'.join(
            textwrap.fill(linea, 24) for linea in lineas)
        return '╟' + textoWrapeado.replace('\n', '\n╟')

    def generarAvisoDiaDeComienzo(self, materia):
        diasDeComienzo = self.diasDeComienzo(materia)
        hayDiasDeComienzo = self.hayDiasDeComienzo(materia)
        aviso = diasDeComienzo if hayDiasDeComienzo else 'Nada publicado'
        return self.tabular(aviso)

    def generarAvisoHorarios(self, materia):
        horarios = self.horarios(materia)
        aviso = horarios if self.hayHorarios(materia) else 'Nada publicado'
        return self.tabular(aviso)

    def generarAvisos(self, materia):
        diasDeComienzo = self.generarAvisoDiaDeComienzo(materia)
        horarios = self.generarAvisoHorarios(materia)
        aviso = '• {}\n╔HORARIOS:\n{}\n╞\n╟COMIENZO:\n{}'.format(
            materia, horarios, diasDeComienzo)
        return aviso

    def crearSoup(self):
        ssl._create_default_https_context = ssl._create_unverified_context
        request = urllib.request.Request(
            'https://gestiondeaulas.info.unlp.edu.ar/cursadas/')
        html = urllib.request.urlopen(request).read()
        return BeautifulSoup(html, 'html.parser')
