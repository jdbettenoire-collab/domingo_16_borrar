from get_alpaca_data import get_alpaca_data, save_alpaca_data
from plot_chart import create_close_chart


def main() -> None:
    print("Descargando datos de AAPL desde Alpaca...")
    apple_data = get_alpaca_data()
    data_file = save_alpaca_data(apple_data)
    print(f"Datos guardados en: {data_file}")

    print("Generando gráfico del precio de cierre...")
    chart_file = create_close_chart(data_file)
    print(f"Gráfico guardado en: {chart_file}")


if __name__ == "__main__":
    main()
