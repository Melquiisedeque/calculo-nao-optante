from flask import Flask, request, jsonify
import re
import os

app = Flask(__name__)

def interpretar_valor(valor_texto):
    """
    Interpreta o valor fornecido pelo cliente, em diferentes formatos numéricos,
    e converte para um número float.
    """
    try:
        valor_texto = valor_texto.strip()
        valor_texto = valor_texto.replace(',', '.')
        valor_texto = valor_texto.replace('.', '', valor_texto.count('.') - 1)
        return float(valor_texto)
    except ValueError:
        raise ValueError("Digite somente números no formato válido, como: 1000,00 ou 1000.00")

def calcular_valor_fgts(saldo_fgts, mes_aniversario):
    """
    Calcula o valor liberado com base no saldo FGTS, mês atual e mês de aniversário.
    """
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

    valor_proporcional = (valor_base / 1000) * saldo_fgts
    return round(valor_proporcional, 2)

def formatar_valor(valor):
    """
    Formata um número no estilo brasileiro, com separador de milhar e decimal.
    """
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

@app.route('/calcular_fgts', methods=['POST'])
def calcular_fgts():
    try:
        data = request.json
        saldo = data.get("saldo_fgts")
        mes_aniversario = data.get("mes_aniversario")

        if not saldo or not mes_aniversario:
            return jsonify({"erro": "Os campos 'saldo_fgts' e 'mes_aniversario' são obrigatórios."}), 400

        saldo_fgts = interpretar_valor(str(saldo))
        if len(mes_aniversario) != 2 or not mes_aniversario.isdigit() or not (1 <= int(mes_aniversario) <= 12):
            return jsonify({"erro": "Mês inválido! Digite no formato MM (01-12)."}), 400

        valor_liberado = calcular_valor_fgts(saldo_fgts, mes_aniversario)

        # Formatar os valores no formato brasileiro
        saldo_formatado = formatar_valor(saldo_fgts)
        valor_liberado_formatado = formatar_valor(valor_liberado)

        return jsonify({
            "saldo_fgts": saldo_formatado,
            "mes_aniversario": mes_aniversario,
            "valor_liberado": valor_liberado_formatado
        })
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400
    except Exception as e:
        return jsonify({"erro": "Erro interno do servidor.", "detalhes": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5004))
    app.run(host='0.0.0.0', port=port)
