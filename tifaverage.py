import os
import glob
import numpy as np
import rasterio
from dash import dcc, html, Dash
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc


# 计算多个tif文件的均值并生成一个新的均值tif文件
def calc_mean_tif(tif_files, output_tif):
    # 打开第一个tif文件，获取元数据
    with rasterio.open(tif_files[0]) as src:
        meta = src.meta
        data_sum = src.read(1).astype(float)  # 读取第一个tif文件的数据作为初始累加值

    # 遍历剩余的tif文件进行累加
    for tif_file in tif_files[1:]:
        with rasterio.open(tif_file) as src:
            data_sum += src.read(1).astype(float)

    # 计算均值
    mean_data = data_sum / len(tif_files)

    # 更新元数据
    meta.update(dtype=rasterio.float32)

    # 将均值数据写入新的tif文件
    with rasterio.open(output_tif, 'w', **meta) as dst:
        dst.write(mean_data.astype(rasterio.float32), 1)


# 创建Dash应用程序
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("TIF 文件均值计算工具"), className="text-center my-3")
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Label("输入TIF文件夹路径:"),
            dbc.Input(id="tif-folder", type="text", placeholder="输入TIF文件夹路径", style={'margin-bottom': '10px'}),
            dbc.Label("输出均值TIF文件路径:"),
            dbc.Input(id="output-tif", type="text", placeholder="输出均值TIF文件路径", style={'margin-bottom': '10px'}),
            dbc.Button("开始处理", id="process-button", color="primary", className="mt-3"),
            html.Div(id="output-message", className="mt-3")
        ], width=6)
    ])
])


@app.callback(
    Output("output-message", "children"),
    Input("process-button", "n_clicks"),
    State("tif-folder", "value"),
    State("output-tif", "value")
)
def process_files(n_clicks, tif_folder, output_tif):
    if not n_clicks:
        return ""

    if not tif_folder or not output_tif:
        return "请提供所有路径。"

    try:
        tif_files = glob.glob(os.path.join(tif_folder, '*.tif'))  # 获取tif文件列表

        if not tif_files:
            return "指定的文件夹中没有找到tif文件。"

        # 计算均值并生成新的tif文件
        calc_mean_tif(tif_files, output_tif)
        return f'均值TIF文件已保存到 {output_tif}'

    except Exception as e:
        return f"处理过程中发生错误: {str(e)}"


if __name__ == '__main__':
    app.run_server(debug=True)
