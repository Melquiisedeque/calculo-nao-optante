from flask import Flask, request, jsonify
import re
from datetime import datetime

app = Flask(__name__)

# Função para interpretar valores numéricos
def interpretar_valor(valor_texto):
    try:
        # Padronizar a entrada (remover espaços e caracteres irrelevantes)
        valor_texto = valor_texto.strip()

        # Substituir vírgulas por pontos
        valor_texto = valor_texto.replace(',', '.')

        # Remover separadores de milhar (pontos)
        valor_texto = valor_texto.replace('.', '')

        # Adicionar o separador decimal correto
        if '.' in valor_texto:
            partes = valor_texto.split('.')
            valor_texto = f"{''.join(partes[:-1])}.{partes[-1]}"

        # Converter para float
        return float(valor_texto)
    except ValueError:
        raise ValueError("Digite somente números no formato válido, como: 1000,00 ou 1000.00")

# Função para calcular o valor do FGTS
def calcular_valor_fgts(saldo_fgts, mes_aniversario):
    valores_esperados = {
        "01": 732.31,
        "02": 716.81,
        "03": 703.05,
        "04": 688.12,
        "05": 673.95,
        "06": 659.59,
        "07": 645.95,
        "08": 632.12,
        "09": 618.59,
        "10": 605.72,
        "11": 592.69,
        "12": 580.32
    }

    valor_base = valores_esperados.get(mes_aniversario)
    if valor_base is None:
        raise ValueError(f"O mês '{mes_aniversario}' não foi encontrado nos valores esperados.")

    return round((valor_base / 1000) * saldo_fgts, 2)

# Endpoint para cálculo do FGTS
@app.route('/calcular_fgts', methods=['POST'])
def calcular_fgts():
    try:
        data = request.json
        saldo = data.get("saldo_fgts")
        mes_aniversario = data.get("mes_aniversario")

        if not saldo or not mes_aniversario:
            return jsonify({"erro": "Os campos 'saldo_fgts' e 'mes_aniversario' são obrigatórios."}), 400

        # Interpretar o saldo e validar o mês
        saldo_fgts = interpretar_valor(str(saldo))
        if len(mes_aniversario) != 2 or not mes_aniversario.isdigit() or not (1 <= int(mes_aniversario) <= 12):
            return jsonify({"erro": "Mês inválido! Digite no formato MM (01-12)."}), 400

        # Calcular o valor liberado
        valor_liberado = calcular_valor_fgts(saldo_fgts, mes_aniversario)

        return jsonify({
            "saldo_fgts": saldo_fgts,
            "mes_aniversario": mes_aniversario,
            "valor_liberado": valor_liberado
        })
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400
    except Exception as e:
        return jsonify({"erro": "Erro interno do servidor.", "detalhes": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5004)
