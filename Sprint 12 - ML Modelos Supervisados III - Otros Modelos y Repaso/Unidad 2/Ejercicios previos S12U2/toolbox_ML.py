# toolbox_ML.py

import pandas as pd
from scipy.stats import pearsonr

def describe_df(df):
    """
    Genera una descripción del DataFrame con información sobre las columnas.

    Argumentos:
    df (pd.DataFrame): DataFrame que se desea describir.

    Retorna:
    pd.DataFrame: DataFrame con información sobre cada columna:
        - Nombre de la columna
        - Tipo de dato
        - Porcentaje de valores nulos
        - Cantidad de valores únicos
        - Porcentaje de cardinalidad
    """
    description = pd.DataFrame({
        "Column Name": df.columns,
        "Data Type": [df[col].dtype for col in df.columns],
        "Null Percentage (%)": [(df[col].isnull().sum() / len(df)) * 100 for col in df.columns],
        "Unique Values": [df[col].nunique() for col in df.columns],
        "Cardinality (%)": [(df[col].nunique() / len(df)) * 100 for col in df.columns],
    })
    return description

def tipifica_variables(df, umbral_categoria, umbral_continua):
    """
    Clasifica las variables de un DataFrame en tipos sugeridos.

    Argumentos:
    df (pd.DataFrame): DataFrame cuyas variables se desean clasificar.
    umbral_categoria (int): Umbral para considerar una variable como categórica.
    umbral_continua (float): Umbral para considerar una variable como continua.

    Retorna:
    pd.DataFrame: DataFrame con columnas:
        - "nombre_variable": Nombre de las columnas originales.
        - "tipo_sugerido": Tipo sugerido para cada variable.
    """
    resultado = []

    for col in df.columns:
        cardinalidad = df[col].nunique()
        porcentaje_cardinalidad = cardinalidad / len(df)

        if cardinalidad == 2:
            tipo = "Binaria"
        elif cardinalidad < umbral_categoria:
            tipo = "Categórica"
        elif porcentaje_cardinalidad >= umbral_continua:
            tipo = "Numérica Continua"
        else:
            tipo = "Numérica Discreta"

        resultado.append({"nombre_variable": col, "tipo_sugerido": tipo})

    return pd.DataFrame(resultado)

def get_features_num_regression(df, target_col, umbral_corr, pvalue=None):
    """
    Obtiene columnas numéricas del DataFrame cuya correlación con una columna objetivo supera un umbral.

    Argumentos:
    df (pd.DataFrame): DataFrame con los datos.
    target_col (str): Nombre de la columna objetivo (debe ser numérica).
    umbral_corr (float): Umbral de correlación (valor absoluto) entre 0 y 1.
    pvalue (float, opcional): Nivel de significancia estadística para el test de correlación.

    Retorna:
    list: Lista de columnas que cumplen las condiciones de correlación y significancia.
    """
    if not (0 <= umbral_corr <= 1):
        print("Error: umbral_corr debe estar entre 0 y 1.")
        return None

    if pvalue is not None and not (0 <= pvalue <= 1):
        print("Error: pvalue debe estar entre 0 y 1 o ser None.")
        return None

    if target_col not in df.columns or not np.issubdtype(df[target_col].dtype, np.number):
        print("Error: target_col no es una columna numérica válida del DataFrame.")
        return None

    numeric_cols = df.select_dtypes(include=[np.number]).columns
    correlations = []

    for col in numeric_cols:
        if col != target_col:
            corr, p_val = pearsonr(df[target_col].dropna(), df[col].dropna())
            if abs(corr) > umbral_corr:
                if pvalue is None or p_val <= pvalue:
                    correlations.append(col)

    return correlations

def plot_features_num_regression(df, target_col="", columns=[], umbral_corr=0, pvalue=None):
    """
    Genera pairplots de las columnas numéricas seleccionadas en base a la correlación con una columna objetivo.

    Argumentos:
    df (pd.DataFrame): DataFrame con los datos.
    target_col (str): Nombre de la columna objetivo.
    columns (list of str): Lista de columnas a considerar.
    umbral_corr (float): Umbral de correlación (valor absoluto).
    pvalue (float, opcional): Nivel de significancia estadística para el test de correlación.

    Retorna:
    list: Lista de columnas que cumplen las condiciones de correlación y significancia.
    """
    if not isinstance(columns, list):
        print("Error: columns debe ser una lista.")
        return None

    if not (0 <= umbral_corr <= 1):
        print("Error: umbral_corr debe estar entre 0 y 1.")
        return None

    if pvalue is not None and not (0 <= pvalue <= 1):
        print("Error: pvalue debe estar entre 0 y 1 o ser None.")
        return None

    if target_col not in df.columns or not np.issubdtype(df[target_col].dtype, np.number):
        print("Error: target_col no es una columna numérica válida del DataFrame.")
        return None

    if not columns:
        columns = df.select_dtypes(include=[np.number]).columns.tolist()

    valid_columns = []

    for col in columns:
        if col != target_col:
            corr, p_val = pearsonr(df[target_col].dropna(), df[col].dropna())
            if abs(corr) > umbral_corr:
                if pvalue is None or p_val <= pvalue:
                    valid_columns.append(col)

    if not valid_columns:
        print("No se encontraron columnas que cumplan las condiciones especificadas.")
        return []

    # Dividir las columnas en grupos de máximo 5 para los pairplots
    max_columns = 5
    valid_columns = [target_col] + valid_columns

    for i in range(1, len(valid_columns), max_columns - 1):
        subset = valid_columns[:1] + valid_columns[i:i + max_columns - 1]
        sns.pairplot(df[subset].dropna(), diag_kind="kde")
        plt.show()

    return valid_columns[1:]


import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency

def get_features_cat_regression(dataframe, target_col, pvalue=0.05):
    """
    Identifica columnas categóricas (numéricas con baja cardinalidad o explícitamente categóricas)
    que tienen una relación significativa con una columna numérica objetivo usando la prueba de Chi-cuadrado.

    Parámetros:
    - dataframe: pd.DataFrame. El DataFrame de entrada.
    - target_col: str. Nombre de la columna objetivo, debe ser numérica.
    - pvalue: float. Nivel de significancia para la prueba Chi-cuadrado.

    Retorna:
    - Una lista de columnas categóricas significativas o None si no se encuentran.
    """
    # Dividir columnas explícitamente categóricas y numéricas
    explicit_categorical_cols = [col for col in dataframe.select_dtypes(include=['object', 'category']).columns if col != target_col]
    potential_categorical_cols = [col for col in dataframe.select_dtypes(include=[np.number]).columns
                                   if col != target_col and dataframe[col].nunique() <= 10]

    # Combinar ambas listas
    all_categorical_cols = explicit_categorical_cols + potential_categorical_cols

    if not all_categorical_cols:
        print("Error: No se encontraron columnas categóricas o numéricas con baja cardinalidad.")
        return None

    significant_features = []

    for col in all_categorical_cols:
        try:
            # Crear una tabla de contingencia
            contingency_table = pd.crosstab(dataframe[col], pd.cut(dataframe[target_col], bins=5))

            # Realizar la prueba de Chi-cuadrado
            chi2, p, dof, expected = chi2_contingency(contingency_table)

            # Comprobar si el p-valor es menor que el umbral dado
            if p < pvalue:
                significant_features.append(col)

        except Exception as e:
            print(f"Advertencia: Error al procesar la columna '{col}': {e}")

    if not significant_features:
        print("No se encontraron columnas categóricas con una relación significativa con el target.")
        return []

    return significant_features

import seaborn as sns
import matplotlib.pyplot as plt

def plot_features_cat_regression(dataframe, target_col, categorical_columns, with_individual_plot=False):
    """
    Dibuja histogramas de la relación entre las columnas categóricas y la columna objetivo
    utilizando subplots para mostrar todas las gráficas juntas en una cuadrícula.

    Parámetros:
    - dataframe: pd.DataFrame. El DataFrame con los datos.
    - target_col: str. Nombre de la columna objetivo numérica.
    - categorical_columns: list. Lista de columnas categóricas significativas obtenidas.
    - with_individual_plot: bool. Si True, genera solo gráficos individuales para cada columna.

    Retorna:
    - None. Dibuja los histogramas en pantalla.
    """
    if not categorical_columns:
        print("No se proporcionaron columnas categóricas para graficar.")
        return

    # Si se solicita gráficos individuales, no crear subplots
    if with_individual_plot:
        for col in categorical_columns:
            try:
                plt.figure(figsize=(10, 6))
                sns.countplot(
                    data=dataframe,
                    x=target_col,
                    hue=col,
                    palette="tab10"
                )
                plt.title(f"Histograma individual de '{target_col}' agrupado por '{col}'", fontsize=14)
                plt.xlabel(target_col, fontsize=12)
                plt.ylabel("Frecuencia", fontsize=12)
                plt.xticks(ticks=[0, 1], labels=["0", "1"], fontsize=10)
                plt.grid(axis='y', linestyle='--', alpha=0.7)
                plt.legend(title=col, fontsize=10)
                plt.tight_layout()
                plt.show()
            except Exception as e:
                print(f"Error al graficar la columna '{col}': {e}")
        return  # Salir de la función tras generar gráficos individuales

    # Crear subplots si no se solicitan gráficos individuales
    num_cols = len(categorical_columns)
    cols_per_row = 2  # Número de columnas por fila
    rows = (num_cols + cols_per_row - 1) // cols_per_row  # Calcular el número de filas necesarias

    fig, axes = plt.subplots(nrows=rows, ncols=cols_per_row, figsize=(15, 6 * rows), constrained_layout=True)
    axes = axes.flatten()  # Aplanar la matriz de ejes para iterar fácilmente

    for i, col in enumerate(categorical_columns):
        try:
            sns.countplot(
                data=dataframe,
                x=target_col,
                hue=col,
                palette="tab10",
                ax=axes[i]
            )
            axes[i].set_title(f"Histograma de '{target_col}' agrupado por '{col}'", fontsize=14)
            axes[i].set_xlabel(target_col, fontsize=12)
            axes[i].set_ylabel("Frecuencia", fontsize=12)
            
            axes[i].grid(axis='y', linestyle='--', alpha=0.7)
            axes[i].legend(title=col, fontsize=10)

        except Exception as e:
            print(f"Error al graficar la columna '{col}': {e}")

    # Eliminar ejes vacíos si hay menos subplots que espacios disponibles
    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])

    plt.show()


# EXTRA EXTRA EXTRA 

def seleccionar_features(df, target, umbral_correlacion=0.15, umbral_correlacion_entre_features=0.7):

    # Filtrar solo las columnas numéricas
    df_numeric = df.select_dtypes(include=[np.number])
    
    # Calcular la matriz de correlación
    correlacion = df_numeric.corr()

    # Verificar que el target esté en la matriz de correlación
    if target not in correlacion.columns:
        raise ValueError(f"El target '{target}' no se encuentra en el DataFrame o no es numérico.")

    # Seleccionar las features con correlación mayor al umbral con el target
    correlacion_target = correlacion[target].abs()
    features_sel = correlacion_target[correlacion_target > umbral_correlacion].index.tolist()

    # Remover el target de la lista de features
    if target in features_sel:
        features_sel.remove(target)

    # Filtrar las features con alta correlación entre ellas
    features_a_eliminar = []
    for i, feat1 in enumerate(features_sel):
        for feat2 in features_sel[i+1:]:
            if abs(correlacion.loc[feat1, feat2]) > umbral_correlacion_entre_features:
                if feat1 not in features_a_eliminar:
                    features_a_eliminar.append(feat2)  # Eliminar la segunda feature

    # Filtrar la lista de features seleccionadas
    features_sel = [feat for feat in features_sel if feat not in features_a_eliminar]
    
    return features_sel




