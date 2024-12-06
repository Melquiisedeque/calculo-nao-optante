from flask import Flask, request, jsonify

app = Flask(__name__)

# Função para interpretar valores numéricos
def interpretar_valor(valor_texto):
    """
    Interpreta o valor fornecido pelo cliente, em diferentes formatos numéricos,
    e converte para um número float.
    """
    try:
        valor_texto = valor_texto.strip()
        valor_texto = valor_texto.replace(',', '.')  # Substituir vírgulas por pontos
        valor_texto = valor_texto.replace('.', '', valor_texto.count('.') - 1)  # Remover separadores de milhar

        return float(valor_texto)
    except ValueError:
        raise ValueError("Digite somente números no formato válido, como: 1000,00 ou 1000.00")

# Função para calcular o valor do FGTS
def calcular_valor_fgts(saldo_fgts, mes_aniversario):
    """
    Calcula o valor liberado com base no saldo FGTS e no mês de aniversário.
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

    return round((valor_base / 1000) * saldo_fgts, 2)

# Endpoint para cálculo do FGTS
@app.route('/calcular_fgts', methods=['POST'])
def calcular_fgts():
    try:
        data = request.json
        if not data:
            return jsonify({"erro": "Requisição inválida. Certifique-se de enviar um JSON válido."}), 400

        saldo = data.get("saldo_fgts")
        mes_aniversario = data.get("mes_aniversario")

        if not saldo or not mes_aniversario:
            return jsonify({"erro": "Os campos 'saldo_fgts' e 'mes_aniversario' são obrigatórios."}), 400

        saldo_fgts = interpretar_valor(str(saldo))
        if len(mes_aniversario) != 2 or not mes_aniversario.isdigit() or not (1 <= int(mes_aniversario) <= 12):
            return jsonify({"erro": "Mês inválido! Digite no formato MM (01-12)."}), 400

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
    # Use a porta fornecida pelo Railway, com fallback para 5000
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
