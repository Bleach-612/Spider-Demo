# 导入需要的包
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker 
import matplotlib.animation as animation
from IPython.display import HTML

new_name = ['Series Name', 'Series Code', 'Country Name', 'Country Code', '1990', '2000', '2010', '2011', '2012',
            '2013', '2014', '2015', '2016', '2017', '2018', '2019']

df = pd.read_csv("./GDP.csv", names=new_name, header=0, na_values='..')
df.head(5)

df.drop(['Series Name', 'Series Code', '2019'], axis=1, inplace=True)  # 2019的数据还未统计，予以删除，删除指标名称列和指标编码列
df[['1990', '2000', '2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018']].astype('float64',errors='ignore')


# 将1990至2018年排在前十的国家都找出来，集合去重转为列表
years = ['1990', '2000', '2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018']
country = set()
for i in range(len(years)):
    year = years[i]
    dff = (df[['Country Name', 'Country Code', year]].sort_values(by=year, ascending=False).head(10))
    coun = dff['Country Name'].tolist()
    coun = set(coun)
    country = country | coun
country = list(country)
country.sort()


# 为各国设置颜色
colors = dict(zip(country, ['#CCFFFF', '#CCFFCC', '#FF3366', '#99FFFF', '#CCFF99', '#FFFF99',
                            '#99CCCC', '#FF6666', '#CCCCFF', '#FFCCFF', '#FFCCCC', '#FFCC99']))

fig, ax = plt.subplots(figsize=(15, 8))


def draw_barchart(year):
    dff = (df[['Country Name', 'Country Code', year]].sort_values(by=year, ascending=False).head(10))
    dff = dff[::-1]
    # 为作图方便将数值除以10^13
    dff[year] = dff[year] / 10 ** 13
    ax.clear()
    ax.barh(dff['Country Name'], dff[year], color=[colors[x] for x in dff['Country Name']])
    dx = dff[year].max() / 200
    # 添加标注
    for i, (value, name) in enumerate(zip(dff[year], dff['Country Name'])):
        # enumerate枚举对象，一个索引序列，同时列出数据和数据下标
        ax.text(value - dx, i, name, size=12, weight=600, ha='right', va='bottom')  # 国家名称
        ax.text(value - dx, i - 0.25, value, size=10, color='#444444', ha='right', va='baseline')  # GDP值/10^13

    # 添加年份
    ax.text(1, 0.4, year, transform=ax.transAxes, color='#777777', size=46, ha='right', weight=800)
    # 添加指标
    ax.text(0, 1.06, 'GDP (constant 2010 US$)ⅹ10^13', transform=ax.transAxes, size=12, color='#777777')
    # 横坐标保持两位小数,位于上方，颜色以及字体大小
    # ax.xaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))
    ax.xaxis.set_ticks_position('top')
    ax.tick_params(axis='x', colors='#777777', labelsize=12)
    # 去除纵坐标
    ax.set_yticks([])
    # 设置自动缩放
    ax.margins(0, 0.01)
    # 设置网格线
    ax.grid(which='major', axis='x', linestyle='-')
    # 网格线置地
    ax.set_axisbelow(True)
    # 标题
    ax.text(0, 1.12, 'GDP rankings of countries in the world from 1990 to 2018',
            transform=ax.transAxes, size=24, weight=600, ha='left')
    # 右下角标注
    ax.text(1, 0, 'by Anran', transform=ax.transAxes, ha='right',
            color='#777777', bbox=dict(facecolor='white', alpha=0.8, edgecolor='white'))
    # 去除外边框
    plt.box(False)


draw_barchart('2018')

fig, ax = plt.subplots(figsize=(15, 8))
animator = animation.FuncAnimation(fig, draw_barchart, frames=years)
animator.to_html5_video()
animator.save('./GDP.mp4')
# HTML(animator.to_jshtml())
# plt.show()

# https://mp.weixin.qq.com/s/KaB_7oXZf0_IV97y0pRPmQ



