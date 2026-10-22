#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""農学系2年生の電磁波→植生指数の梯子に使う13図を再生成する。
実行: python -I scripts/figures/make_charts.py [--only 03]
測定データではない曲線は模式図と明記。根拠は同リポジトリのR1/R3/R4。
バンド仕様は代表値（矩形近似）で、機体別応答関数ではない。
"""
from pathlib import Path
import os
import sys
sys.dont_write_bytecode = True
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
# この環境の旧matplotlibを変更せず、作業領域内の指定版を優先する。
if (HERE / '_vendor').is_dir():
    sys.path.insert(0, str(HERE / '_vendor'))
os.environ['MPLCONFIGDIR'] = str(HERE / '_mplconfig')
import argparse
import json
import warnings
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager, ft2font
from matplotlib.patches import Rectangle, Ellipse, FancyArrowPatch
from matplotlib.lines import Line2D
from matplotlib.text import Text
from PIL import Image

BG, NAVY, TEAL, ORANGE, GRAY = '#FAF9F5', '#1F4E79', '#13877B', '#BD512B', '#8A8A8A'
plt.rcParams.update({'font.family': ['Yu Gothic', 'Meiryo', 'MS Gothic', 'sans-serif'],
    'axes.unicode_minus': False, 'font.size': 17, 'axes.labelsize': 17,
    'xtick.labelsize': 16, 'ytick.labelsize': 16, 'legend.fontsize': 15,
    'figure.facecolor': BG, 'axes.facecolor': BG, 'text.color': NAVY,
    'axes.labelcolor': NAVY, 'xtick.color': NAVY, 'ytick.color': NAVY,
    'axes.edgecolor': GRAY, 'axes.spines.top': False, 'axes.spines.right': False,
    'lines.linewidth': 2.3, 'savefig.facecolor': BG})
warnings.filterwarnings('error', message=r'Glyph .* missing from font')
OUT = ROOT / 'materials/slides/2026_農業とテクノロジ_RS/figures/charts'
QA = ROOT / 'notes/codex'
# SI標準値: c=299792458 m/s, h=6.62607015e-34 J s, k=1.380649e-23 J/K。
C, H, K = 299792458.0, 6.62607015e-34, 1.380649e-23
SIGMA = 5.670374419e-8  # W m^-2 K^-4（標準値）
WIEN = 2897.771955  # µm K。講義では2898へ丸める。
SOLAR = 1361.0  # W/m²、1 auでの代表的太陽放射照度（固定近似）

def planck(lam_um, temperature):
    """Bλ=2hc²/λ⁵ / [exp(hc/(λkT))-1]、戻り値 W m^-2 sr^-1 µm^-1。"""
    lam = np.asarray(lam_um, dtype=float) * 1e-6
    z = H * C / (lam * K * temperature)
    # exp(-z)/(1-exp(-z))で指数オーバーフローを避ける。
    return (2 * H * C*C / lam**5) * np.exp(-z) / (-np.expm1(-z)) * 1e-6

def gauss(x, mean, width):
    return np.exp(-0.5 * ((x - mean) / width)**2)

# 大気の模式吸収: (分子,中心µm,標準偏差µm,基線からの相対吸収深さ)。
# 位置は入門的な吸収帯。幅・深さは見やすさのための任意設定で実測ではない。
# 水蒸気は0.94/1.14を弱中、1.38/1.87/2.7/6.3を強吸収にする。
# CO2は2.7/4.3/15、O3はUVと9.6、O2は0.76に谷を置く。
ABSORPTION = [('H₂O', .94,.024,.35), ('H₂O',1.14,.035,.38),
 ('H₂O',1.38,.075,.97), ('H₂O',1.87,.10,.98), ('H₂O',2.7,.22,.97),
 ('H₂O',6.3,.85,.995), ('CO₂',2.7,.09,.80), ('CO₂',4.3,.13,.98),
 ('CO₂',15,1.0,.99), ('O₃',.255,.04,.995), ('O₃',9.6,.28,.65),
 ('O₂',.76,.006,.45)]

def atmosphere(x):
    """晴天大気の模式的な直達透過率。雲・エアロゾル・多重散乱は計算しない。"""
    x=np.asarray(x)
    # UV端を吸収し、レイリー散乱による短波長側の低下も弱く模す。
    t=.94*np.exp(-.006/x**4) / (1+np.exp(-(x-.305)/.012))
    for _,mu,s,d in ABSORPTION:
        t *= 1-d*gauss(x,mu,s)
    return np.clip(t,0,1)

def reflectance(x):
    """R4の葉の機構を再現。葉・土・水・雪の曲線は教示用で実測ではない。"""
    x=np.asarray(x)
    # 葉: 青450nm/赤670nmの吸収、緑550nmの山、725nm中心の急な立上り。
    # NIRは約46%。水吸収1450nmで深さ78%、1950nmで92%。
    v=.065+.055*gauss(x,.55,.042)-.04*gauss(x,.45,.025)-.045*gauss(x,.67,.027)
    v+=.40/(1+np.exp(-(x-.725)/.013))
    v*=1-.78*gauss(x,1.45,.065)
    v*=1-.92*gauss(x,1.95,.10)
    v*=1-.35*np.clip((x-1.3)/1.2,0,1)
    # 乾いた土は15→40%、水は可視数%でNIR以降ほぼ0。
    soil=.15+.25*(x-.4)/2.1
    water=.025*gauss(x,.49,.12)/(1+np.exp((x-.72)/.025))+.001
    # 雪は可視約90%（指定縦軸70%を超える）。上限超過を注記し切り詰めない。
    # 氷の吸収と粒径依存を単純化: 1.03/1.25弱、1.5/2.0強。
    snow=.90/(1+np.exp((x-1.25)/.24))+.015
    snow*=1-.20*gauss(x,1.03,.055)
    snow*=1-.72*gauss(x,1.50,.10)
    snow*=1-.88*gauss(x,2.00,.12)
    return [np.clip(y,0,1)*100 for y in (v,soil,water,snow)]

def base(left=.115,bottom=.23,right=.97,top=.95):
    fig,ax=plt.subplots(figsize=(8,4.5),dpi=200)
    fig.subplots_adjust(left=left,bottom=bottom,right=right,top=top)
    ax.grid(axis='y',color=GRAY,alpha=.16,lw=.7)
    return fig,ax

def visible(ax,alpha=.10,ymin=0,ymax=1):
    # 虹色は可視帯の物理的意味がある場所だけに使用。
    colors=['#7545A0','#3155BC','#2587A7','#5A9D47','#D4B347','#D07C3D','#B64436']
    for a,b,col in zip(np.linspace(.4,.7,8)[:-1],np.linspace(.4,.7,8)[1:],colors):
        ax.axvspan(a,b,ymin=ymin,ymax=ymax,color=col,alpha=alpha,lw=0)

def note(fig,text,y=.035):
    fig.text(.97,y,text,ha='right',va='bottom',fontsize=12,color=GRAY)

def schematic(fig):
    fig.text(.012,.985,'模式図',ha='left',va='top',fontsize=12,color=GRAY)  # 左上。右下は脚注と重なる

def wavelength_axis(ax,limits,log=False,ticks=None):
    ax.set_xlim(*limits)
    if log: ax.set_xscale('log')
    ax.set_xlabel('波長 (µm)')
    if ticks is not None:
        ax.set_xticks(ticks,labels=[f'{a:g}' for a in ticks])
        ax.minorticks_off()

def chart_01():
    """段1: 可視は電磁波の狭い一部。RSの観測帯を拡大軸でつなぐ。"""
    fig=plt.figure(figsize=(8,4.5),dpi=200)
    ax=fig.add_axes([.08,.51,.88,.36]); ax.set_xscale('log'); ax.set_xlim(1e-12,1e3)
    ax.set_ylim(0,1); ax.set_yticks([]); ax.grid(False)
    bands=[(1e-12,1e-11,'γ線',GRAY),(1e-11,1e-8,'X線',NAVY),
      (1e-8,4e-7,'紫外',TEAL),(4e-7,7e-7,'',ORANGE),
      (7e-7,1e-3,'赤外',ORANGE),(1e-3,1,'マイクロ波',TEAL),(1,1e3,'電波',NAVY)]
    for a,b,t,c in bands:
        ax.axvspan(a,b,ymin=.25,ymax=.60,color=c,alpha=.22)
        if t: ax.text(np.sqrt(a*b),.43,t,ha='center',va='center',fontsize=14)
    for a,b,c in zip(np.linspace(4e-7,7e-7,8)[:-1],np.linspace(4e-7,7e-7,8)[1:],['#7545A0','#3155BC','#2587A7','#5A9D47','#D4B347','#D07C3D','#B64436']):
        ax.axvspan(a,b,ymin=.25,ymax=.60,color=c,lw=0)
    ax.annotate('可視光はほんの一部',xy=(5.5e-7,.60),xytext=(4e-7,.89),
        ha='center',fontsize=17,arrowprops={'arrowstyle':'-','color':NAVY})
    for x,t,y in [(1e-10,'レントゲン',.04),(9.4e-7,'リモコン',.04),(.122,'電子レンジ',.76),(.2,'携帯電話',.04)]:
        ax.text(x,y,t,ha='center',fontsize=13)
    ax.set_xticks([1e-12,1e-9,1e-6,1e-3,1,1e3],['1 pm','1 nm','1 µm','1 mm','1 m','1 km'])
    ax.minorticks_off()
    ax.text(.99,1.13,'区分の境界は慣用的／マイクロ波も電波の一部',transform=ax.transAxes,ha='right',fontsize=13)
    bx=fig.add_axes([.12,.20,.81,.18]); bx.set_xscale('log'); bx.set_xlim(.35,20); bx.set_ylim(0,1); bx.set_yticks([])
    visible(bx,.5)
    for a,b,t,c in [(.7,1.3,'近赤外',TEAL),(1.3,3,'短波長赤外',ORANGE),(3,14,'熱赤外',NAVY)]:
        bx.axvspan(a,b,ymin=.2,ymax=.8,color=c,alpha=.18)
        bx.text(np.sqrt(a*b),.5,t,ha='center',va='center',fontsize=14)
    bx.text(.51,.5,'可視',ha='center',va='center',fontsize=13)
    bx.set_xticks([.4,.7,1.3,3,14],['0.4','0.7','1.3','3','14']); bx.minorticks_off(); bx.set_xlabel('RSで使う光の範囲：波長 (µm)',fontsize=17)
    note(fig,'RSではマイクロ波も利用。熱赤外はここでは3〜14 µmの観測域を表示。',.005)
    return fig

def chart_02():
    """段2: 同じ空間幅、同じ伝播速度で山の間隔と通過回数を比較する。"""
    fig,ax=base(left=.06,bottom=.12,top=.92)
    x=np.linspace(0,8,1200)
    for y,w,c,label in [(2.7,4,NAVY,'長い波長 → 揺れはゆっくり'),(.8,2,TEAL,'短い波長 → 揺れは速い')]:
        ax.plot(x,y+.45*np.sin(2*np.pi*x/w),color=c)
        ax.text(0,y+.84,label,fontsize=19)
        a=w/4; b=a+w
        ax.annotate('',xy=(a,y+.5),xytext=(b,y+.5),arrowprops={'arrowstyle':'<->','color':c})
        ax.text((a+b)/2,y+.57,'1波長',ha='center',fontsize=15)
        ax.annotate('同じ速さ c',xy=(8,y),xytext=(6.5,y+.5),fontsize=15,arrowprops={'arrowstyle':'->','color':c})
    ax.set_xlim(-.15,8.6); ax.set_ylim(-.1,4); ax.axis('off')
    fig.text(.5,.04,'同じ距離を同じ時間で進むと、短い波のほうが多くの山を通す。',ha='center',fontsize=16)
    return fig

def chart_03():
    """段4: 共通の基準で黒体放射を比較し、温度上昇で高く・左へ動く山を示す。"""
    fig,ax=base(); x=np.linspace(.1,3,2500); ref=planck(WIEN/6000,6000)
    visible(ax)
    for t,c,ls in [(3000,GRAY,':'),(4000,NAVY,'--'),(5000,TEAL,'-.'),(6000,ORANGE,'-')]:
        ax.plot(x,planck(x,t)/ref,color=c,ls=ls,label=f'{t} K')
        p=WIEN/t; ax.plot(p,planck(p,t)/ref,'o',color=c,ms=5)
    ax.set_ylim(0,1.08); wavelength_axis(ax,(.1,3),ticks=[.5,1,1.5,2,2.5,3])
    ax.set_ylabel('相対分光放射輝度'); ax.legend(loc='upper right',frameon=False)
    ax.text(.45,1.02,'可視',fontsize=14)
    note(fig,'全曲線を6000 Kのピークで割る。面積が総放射に対応（横軸は線形）。')
    return fig

def chart_04():
    """段5: 太陽と地表の波長スケールを比較。独立規格化から交点は推定しない。"""
    fig,ax=base(bottom=.23,top=.87); x=np.geomspace(.1,100,3000)
    visible(ax); ax.axvspan(.7,1.3,color=TEAL,alpha=.08); ax.axvspan(8,14,color=ORANGE,alpha=.08)
    for t,c,label in [(5772,ORANGE,'太陽 5772 K'),(288,NAVY,'地表 288 K')]:
        p=WIEN/t; ax.plot(x,planck(x,t)/planck(p,t),color=c,label=label)
        ax.annotate(f'{p:.1f} µm',xy=(p,1),xytext=(p*1.8,.86),fontsize=17,
            arrowprops={'arrowstyle':'->','color':c},color=c)
    ax.axvline(3,color=GRAY,ls='--',lw=1.4)
    ax.text(.15,.61,'太陽光の\n反射が主',fontsize=16,bbox={'facecolor':BG,'edgecolor':'none','pad':2})
    ax.text(24,.61,'地表の\n放射が主',fontsize=16)
    ax.text(3.6,.30,'約3 µm\n目安',fontsize=14,color=GRAY)
    wavelength_axis(ax,(.1,100),True,[.1,.5,1,3,10,100]); ax.set_ylim(0,1.10)
    ax.set_ylabel('相対値（各ピーク = 1）')
    ax.legend(loc='upper center',bbox_to_anchor=(.5,1.23),ncol=2,frameon=False)
    for a,t in [(.52,'可視'),(.95,'近赤外'),(10.5,'熱赤外の窓')]: ax.text(a,.07,t,rotation=90 if a<2 else 0,ha='center',fontsize=13)
    note(fig,'規格化：高さを比較しない。約3 µmは日中・常温の概略で、温度・反射率・照明に依存。',.04)
    note(fig,'3〜5 µmは反射と放射が混在。境界は、この2曲線の交点から求めていない。',.005)
    return fig

def chart_05():
    """段6（詳説用）: 吸収の谷と、完全には透明でない大気の窓を示す。"""
    fig,ax=base(bottom=.29,top=.77); x=np.geomspace(.2,15,7000)
    for a,b in [(.4,1.3),(1.5,1.8),(2,2.4),(3.5,4),(8,14)]:
        ax.axvspan(a,b,color=TEAL,alpha=.12,lw=0)
    ax.plot(x,100*atmosphere(x),color=NAVY,lw=1.8)
    # 吸収名は上端で2段に分け、近接する0.76〜1.14の文字衝突を避ける。
    for mu,label,y in [(.255,'O₃',123),(.76,'O₂',123),(.94,'H₂O',111),(1.14,'H₂O',123),
       (1.38,'H₂O',111),(1.87,'H₂O',123),(2.7,'H₂O / CO₂',111),
       (4.3,'CO₂',123),(6.3,'H₂O',111),(9.6,'O₃',123),(14.5,'CO₂',111)]:
        ax.text(mu,y,label,ha='center',fontsize=15)
        ax.plot([mu,mu],[95,y-2],color=GRAY,lw=.6,clip_on=False)
    wavelength_axis(ax,(.2,15),True,[.2,.4,1,2,4,8,15]); ax.set_ylim(0,100)
    ax.set_yticks([0,50,100]); ax.set_ylabel('透過率 (%)')
    fig.text(.13,.94,'青緑の帯：大気の窓（内部にも吸収帯がある）',fontsize=15)
    note(fig,'晴天の直達透過を模した形。水蒸気量・経路長で変わる。',.09)
    note(fig,'右のさらに長波長：多くのマイクロ波は雲を通るが、雨・吸収帯の影響は残る。',.055)
    schematic(fig)
    return fig

def chart_06():
    """段6の本文: 同じ太陽光でも大気の吸収・散乱で地上のスペクトルが変わる。"""
    fig,ax=base(bottom=.27); x=np.linspace(.2,3,5000)
    # π∫Bλdλ=σT^4。全波長積分が1361 W/m²となるよう規格化する。
    toa=SOLAR*np.pi*planck(x,5772)/(SIGMA*5772**4)
    visible(ax)
    ax.plot(x,toa,color=ORANGE,label='大気の外（黒体近似）')
    ax.plot(x,toa*atmosphere(x),color=NAVY,label='地上（模式透過率を掛ける）')
    wavelength_axis(ax,(.2,3),ticks=[.5,1,1.5,2,2.5,3]); ax.set_ylim(0,2200)
    ax.set_ylabel('分光放射照度 (W/m²/µm)'); ax.legend(frameon=False,loc='upper right',fontsize=14)
    note(fig,'地球距離での太陽光、全波長積分1361 W/m²。標準地上スペクトルや実測値ではない。',.075)
    note(fig,'直達光の単純化：散乱光の加算・太陽高度・雲は計算しない。',.04)
    schematic(fig)
    return fig

def chart_07():
    """段9: 葉・土・水・雪を波長ごとの返し方で区別する。雪の上限超過を明記。"""
    fig,ax=base(top=.84); x=np.linspace(.4,2.5,2500); visible(ax)
    for y,c,ls,t in zip(reflectance(x),[TEAL,ORANGE,NAVY,GRAY],['-','--','-.',':'],['健全な植生','乾いた土','水','雪']):
        ax.plot(x,y,color=c,ls=ls,label=t)
    wavelength_axis(ax,(.4,2.5),ticks=[.4,.7,1,1.5,2,2.5]); ax.set_ylim(0,70); ax.set_ylabel('反射率 (%)')
    ax.legend(loc='upper center',bbox_to_anchor=(.5,1.23),ncol=4,frameon=False,fontsize=14)
    ax.annotate('レッドエッジ',xy=(.73,26),xytext=(.84,58),fontsize=15,bbox={'facecolor':BG,'edgecolor':'none','pad':1},arrowprops={'arrowstyle':'->','color':TEAL})
    ax.text(.43,66,'雪の可視反射率は約90%\n（縦軸上限の外）',fontsize=13,color=GRAY)
    for x0 in [1.45,1.95]:
        ax.annotate('水の吸収',xy=(x0,8),xytext=(x0,54),ha='center',fontsize=14,
            arrowprops={'arrowstyle':'->','color':GRAY})
    schematic(fig)
    return fig

# 中心・幅（µm）は代表的公称仕様の矩形近似。S2機体差・実効応答は要確認。
S2=[('B2',.490,.065),('B3',.560,.035),('B4',.665,.030),('B5',.705,.015),
 ('B6',.740,.015),('B7',.783,.020),('B8',.842,.115),('B8A',.865,.020),
 ('B11',1.610,.090),('B12',2.190,.180)]
OLI=[('青',.452,.512),('緑',.533,.590),('赤',.636,.673),('近赤外',.851,.879),
 ('SWIR1',1.566,1.651),('SWIR2',2.107,2.294)]

def chart_08():
    """段10: 連続曲線をバンド平均で測る。混雑する可視/NIRは別の拡大窓で読む。"""
    fig=plt.figure(figsize=(8,4.5),dpi=200)
    # 全域と0.4〜0.95の拡大を横に並べ、帯の矩形重ねを2段に分ける。
    axs=[fig.add_axes([.10,.26,.42,.60]),fig.add_axes([.61,.26,.36,.60])]
    for ax,lim in zip(axs,[(.4,2.5),(.4,.95)]):
        x=np.linspace(*lim,1500); v,s,*_=reflectance(x)
        ax.plot(x,v,color=TEAL,label='植生'); ax.plot(x,s,color=ORANGE,ls='--',label='土')
        for name,c,w in S2:
            ax.axvspan(c-w/2,c+w/2,ymin=0,ymax=.80,color=NAVY,alpha=.035,lw=0)
            ax.axvspan(c-w/2,c+w/2,ymin=.80,ymax=.91,color=NAVY,alpha=.26,lw=.5,ec=NAVY)
        for name,a,b in OLI:
            ax.axvspan(a,b,ymin=0,ymax=.80,color=ORANGE,alpha=.025,lw=0)
            ax.axvspan(a,b,ymin=.94,ymax=1,color=ORANGE,alpha=.30,lw=.5,ec=ORANGE)
        ax.set_xlim(*lim); ax.set_ylim(0,80); ax.set_yticks([0,20,40,60]); ax.set_xlabel('波長 (µm)')
        ax.grid(axis='y',alpha=.15)
    axs[0].set_ylabel('反射率 (%)'); axs[0].set_xticks([.5,1,1.5,2,2.5]); axs[1].set_xticks([.4,.6,.8])
    axs[0].legend(frameon=False,loc='upper right',fontsize=14,bbox_to_anchor=(1,.79))
    for name,c,w in S2:
        if c>1: axs[0].text(c,62,name,ha='center',fontsize=12)
        else:
            y=59 if name in ['B2','B4','B6','B8'] else 51
            axs[1].annotate(name,xy=(c,64),xytext=(c,y),ha='center',fontsize=12,
              arrowprops={'arrowstyle':'-','lw':.6,'color':NAVY})
    fig.text(.10,.94,'帯の上段：Landsat 8/9 OLI   下段：Sentinel-2 MSI',fontsize=15)
    fig.text(.61,.89,'可視〜近赤外を拡大',fontsize=15)
    note(fig,'矩形は公称帯域の近似。機体別の分光応答ではない。数値表は設計書を参照。',.04)
    schematic(fig)
    return fig

def chart_09():
    """段11: 赤とNIRの差を総和で割る意味。反射率と未補正信号を区別する。"""
    fig=plt.figure(figsize=(8,4.5),dpi=200); ax=fig.add_axes([.10,.21,.55,.71])
    red=np.array([.05,.15,.20,.03]); nir=np.array([.50,.30,.30,.01]); xx=np.arange(4)
    ax.bar(xx-.18,100*red,.34,color=ORANGE,label='赤')
    ax.bar(xx+.18,100*nir,.34,color=TEAL,label='近赤外')
    nd=(nir-red)/(nir+red)
    for i,val in enumerate(nd): ax.text(i,max(red[i],nir[i])*100+3,f'{val:.2f}',ha='center',fontsize=18)
    ax.set_xticks(xx,['健全な\n植生','弱った\n植生','裸地','水']); ax.set_ylim(0,68)
    ax.set_ylabel('反射率 (%)'); ax.legend(frameon=False,loc='upper right',fontsize=15)
    ax.text(0,65,'上の数字は NDVI',fontsize=15)
    bx=fig.add_axes([.69,.21,.28,.71]); bx.axis('off')
    bx.text(0,.95,'共通倍率だけなら',fontsize=17,color=NAVY)
    bx.text(0,.78,'同じ畑：未補正信号\n赤 / 近赤外（任意単位）',fontsize=14)
    bx.text(0,.57,'晴れ相当：5 / 50\n曇り相当：2.5 / 25',fontsize=15,linespacing=1.8)
    bx.text(0,.34,'どちらも 0.82',fontsize=19,color=TEAL)
    bx.text(0,.10,'両帯域が半分という仮定。\n真の反射率が半減する\nという意味ではない。',fontsize=13,linespacing=1.5)
    note(fig,'照度・大気・影の影響が現実に全て消えるわけではない。棒の値は説明用の例。',.045)
    schematic(fig)
    return fig

def chart_10():
    """段12: LAI増加に対する感度の違い。数値は比較の形を示す仮定で較正式ではない。"""
    fig,ax=base(); x=np.linspace(0,8,500)
    # R3 §7の定性的記述を任意指数曲線で表す。NDVIはLAI3〜4で概ね飽和。
    ndvi=.15+.72*(1-np.exp(-.95*x)); ndre=.10+.70*(1-np.exp(-.25*x))
    ax.plot(x,ndvi,color=NAVY,label='NDVI'); ax.plot(x,ndre,color=TEAL,label='NDRE（例）')
    ax.axvspan(3,4,color=GRAY,alpha=.10); ax.annotate('NDVIは差が小さくなる',xy=(4,.85),xytext=(3.2,.99),fontsize=16,
      arrowprops={'arrowstyle':'->','color':NAVY})
    ax.set_xlim(0,8); ax.set_ylim(0,1.07); ax.set_xlabel('葉面積指数 LAI (m²/m²)'); ax.set_ylabel('植生指数')
    ax.legend(frameon=False,loc='lower right')
    note(fig,'LAI 3〜4は目安。作物・生育段階・観測条件で変わり、NDREも飽和する。',.035)
    schematic(fig)
    return fig

def chart_11():
    """後続の衛星選択: 代表的な観測間隔と画素サイズ。保証再訪・費用の回帰ではない。"""
    fig,ax=base(left=.12,bottom=.30,top=.93); ax.set_xscale('log'); ax.set_yscale('log')
    ax.set_xlim(.015,5000); ax.set_ylim(.004,25)
    # 薄い対角線は従来型の設計傾向を示すだけ。商用群・UAVは例外となる。
    ax.plot([.07,2500],[12,.013],color=GRAY,alpha=.22,ls='--',lw=1.5,zorder=0)
    pts=[('ひまわり',2000,10/1440,( -10,13),'right'),('MODIS',500,1,(22,-22),'left'),
      ('Sentinel-3 OLCI',300,1.5,(-5,20),'right'),('Landsat 8/9',30,8,(7,6),'left'),
      ('Sentinel-2',10,5,(-6,8),'right'),('PlanetScope',3,1,(10,-19),'left'),
      ('Pelican /\nWorldView Legion',.4,.4,(-16,12),'right'),('ドローン',.032,.02,(6,8),'left')]
    for name,x,y,offset,ha in pts:
        ax.scatter(x,y,s=42,color=TEAL if name in ['ドローン','PlanetScope'] else NAVY,zorder=3)
        ax.annotate(name,xy=(x,y),xytext=offset,textcoords='offset points',ha=ha,fontsize=14)
    ax.hlines(1,250,1000,color=NAVY,lw=2); ax.vlines(300,1,2,color=NAVY,lw=2)
    ax.hlines(.4,.3,.5,color=NAVY,lw=2); ax.vlines(.4,.07,3,color=NAVY,lw=1.3,alpha=.5)
    ax.hlines(.02,.02,.05,color=TEAL,lw=2)
    ax.set_xticks([.03,.3,3,30,300,3000],['0.03','0.3','3','30','300','3000']); ax.minorticks_off()
    ax.set_yticks([10/1440,1/24,1,5,10],['10分','1時間','1日','5日','10日'])
    ax.set_xlabel('空間分解能 (m)  ← 細かい        粗い →'); ax.set_ylabel('再訪・観測間隔（日、対数）')
    note(fig,'R1・一般仕様の近似。商用の縦線＝日内〜数日の概念範囲（保証値ではない）。',.095)
    note(fig,'ドローンの縦位置は便宜的：好きな時に計画するが天候・運用に依存。',.06)
    note(fig,'点線は概念：広く頻繁なら粗く、細かい観測は範囲・費用に制約。普遍的な法則ではない。',.025)
    return fig

def chart_12():
    """後続の歴史: 打上げイベント。予定は破線・白抜き、失敗は×。稼働期間を意味しない。"""
    fig,ax=base(left=.235,bottom=.23,top=.88,right=.98)
    rows=['Landsat 1–5','Landsat 6–9','Landsat Next','SPOT','Terra / Aqua','ALOS','Sentinel-1','Sentinel-2','PlanetScope','EnMAP','NISAR','FLEX']
    colors={'光学':NAVY,'SAR':TEAL,'ハイパー':ORANGE,'蛍光':GRAY}
    # R1にない過去の年は一般的な打上げ記録による補完。報告書に区別する。
    events=[(0,1972,'1','光学'),(0,1975,'2','光学'),(0,1978,'3','光学'),(0,1982,'4','光学'),(0,1984,'5','光学'),
      (1,1993,'6×','光学'),(1,1999,'7','光学'),(1,2013,'8','光学'),(1,2021,'9','光学'),
      (3,1986,'初号機','光学'),(4,1999,'Terra','光学'),(4,2002,'Aqua','光学'),
      (5,2006,'1','光学'),(5,2014,'2','SAR'),(5,2023,'3×','光学'),(5,2024,'4','SAR'),
      (6,2014,'A','SAR'),(6,2016,'B','SAR'),(6,2024,'C','SAR'),(6,2025,'D','SAR'),
      (7,2015,'A','光学'),(7,2017,'B','光学'),(7,2024,'C','光学'),
      (8,2016,'','光学'),(9,2022,'','ハイパー'),(10,2025,'','SAR')]
    for i in range(len(rows)): ax.axhline(i,color=GRAY,alpha=.13,lw=.7)
    for row,year,label,kind in events:
        marker='x' if '×' in label else 'o'; color=colors[kind]
        ax.plot(year,row,marker,color=color,ms=4.5)
        # ラベルは点から離す。近接年は左右・上下へ分け、年の位置は点で保持する。
        offset=(0,5); ha='center'; va='bottom'
        if label=='Terra': offset=(-7,0); ha='right'; va='center'
        elif label=='Aqua': offset=(7,0); ha='left'; va='center'
        elif label=='3×': offset=(-5,5); ha='right'
        elif row==5 and label=='4': offset=(5,5); ha='left'
        elif row==6 and label=='D': offset=(10,5); ha='left'
        elif row==6 and label=='B': offset=(6,5); ha='left'
        ax.annotate(label,xy=(year,row),xytext=offset,textcoords='offset points',
            ha=ha,va=va,fontsize=12,color=color)
    # ALOS-1は光学とSAR両方搭載。二色の点で表示。
    ax.plot(2006,5,'o',mfc='none',mec=TEAL,ms=7,mew=1.2)
    ax.plot([2016,2026],[8,8],color=NAVY,lw=3,alpha=.45)
    ax.annotate('2016〜',xy=(2016,8),xytext=(2008,8.1),fontsize=13)
    # Nextは2030年確定ではない。軸端に計画領域を設け、年を特定しない。
    ax.plot([2028,2030],[2,2],ls='--',color=NAVY,lw=1.7)
    ax.text(2027,2,'計画：時期未定 →',ha='right',va='center',fontsize=13)
    # FLEXは2026-09-15にVega-CでSentinel-3Cと同時に打上げ済み（ESA発表、R3）。実点で描く。
    ax.plot(2026,11,'o',color=GRAY,ms=4.5)
    ax.annotate('2026-09',xy=(2026,11),xytext=(-7,0),textcoords='offset points',
        ha='right',va='center',fontsize=12,color=GRAY)
    ax.set_yticks(range(len(rows)),rows); ax.set_ylim(11.8,-.8); ax.set_xlim(1971,2031)
    ax.set_xticks([1972,1980,1990,2000,2010,2020,2030]); ax.set_xlabel('打上げ年（計画を含む）')
    ax.tick_params(axis='y',length=0,labelsize=16); ax.tick_params(axis='x',labelsize=16)
    handles=[Line2D([],[],marker='o',ls='',color=c,label=k) for k,c in colors.items()]
    fig.legend(handles=handles,loc='upper center',bbox_to_anchor=(.57,1.0),ncol=4,frameon=False,fontsize=14)
    note(fig,'×＝打上げ失敗（Landsat 6・ALOS-3）。ALOS-1は光学＋SAR。破線＝計画。',.025)
    return fig

def chart_13():
    """段8: 赤は色素で吸収、近赤外は葉内の屈折率境界で多重散乱する模式断面。"""
    fig,ax=base(left=.03,bottom=.06,right=.98,top=.97); ax.axis('off'); ax.set_xlim(0,10); ax.set_ylim(0,7)
    for y,h,col,alpha in [(5.3,.16,ORANGE,.25),(4.83,.47,TEAL,.16),(3.30,1.5,TEAL,.10),(1.05,.45,TEAL,.16)]:
        ax.add_patch(Rectangle((.6,y),6.2,h,facecolor=col,alpha=alpha,edgecolor=NAVY,lw=1))
    for i in range(10):
        ax.add_patch(Ellipse((.93+i*.60,4.04),.49,1.34,facecolor=TEAL,alpha=.22,edgecolor=TEAL))
        for z in [3.7,4.1,4.4]: ax.add_patch(Ellipse((.85+i*.60,z),.10,.15,facecolor=TEAL,lw=0))
    # 海綿状組織: 規則格子からずらした細胞と空気の空隙（白）。
    for x,y,w,h in [(1.0,2.8,.8,.5),(2.2,2.6,1,.6),(3.5,2.9,.9,.5),(4.9,2.7,1,.6),(6.0,2.8,.9,.6),
       (1.3,1.9,1.1,.55),(2.9,2.0,.9,.65),(4.1,1.9,1.0,.55),(5.5,1.85,1.1,.55)]:
        ax.add_patch(Ellipse((x,y),w,h,facecolor=TEAL,alpha=.20,edgecolor=NAVY,lw=1))
    for y,label in [(5.46,'クチクラ'),(5.03,'表皮'),(4.0,'柵状組織'),(2.45,'海綿状組織'),(1.25,'下表皮')]:
        ax.text(7.1,y,label,va='center',fontsize=17)
    ax.text(7.1,1.98,'細胞と空気の隙間',fontsize=14)
    ax.add_patch(FancyArrowPatch((1.65,6.1),(2.25,4.1),arrowstyle='-|>',mutation_scale=18,color=ORANGE,lw=3))
    ax.plot(2.25,4.1,'x',color=ORANGE,ms=12,mew=2.5)
    ax.text(.7,6.45,'赤：吸収される',color=ORANGE,fontsize=19)
    points=[(4.7,6.1),(4.15,2.45),(3.6,2.85),(4.9,2.25),(5.65,3.0),(5.2,6.0)]
    for a,b in zip(points[:-1],points[1:]):
        ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=14,color=NAVY,lw=2.3))
    ax.text(4.5,6.45,'近赤外：散乱して戻る',color=NAVY,fontsize=19)
    ax.text(.7,.43,'近赤外は下へ透過する分もある。散乱は細胞壁・空気などの境界で起きる。',fontsize=14)
    schematic(fig)
    return fig

NAMES=['em_spectrum','wavelength_frequency','planck_temperature','sun_earth_two_peaks',
 'atmosphere_windows','solar_spectrum_toa_surface','reflectance_curves','reflectance_with_bands',
 'ndvi_bars','ndvi_saturation','resolution_tradeoff','satellite_timeline','leaf_cross_section']

def verify_physics():
    x=np.geomspace(.01,10000,40000)
    for t in [288,3000,4000,5000,5772,6000]:
        integral=np.pi*np.trapezoid(planck(x,t),x)
        assert np.isclose(integral,SIGMA*t**4,rtol=2e-5), (t,integral)
        peak=x[np.argmax(planck(x,t))]
        assert np.isclose(peak,WIEN/t,rtol=.001)
    assert np.all((atmosphere(x)>=0)&(atmosphere(x)<=1))
    assert np.isclose((.5-.05)/(.5+.05),(.25-.025)/(.25+.025))

def save_checked(fig,index):
    fig.canvas.draw()
    renderer=fig.canvas.get_renderer(); fonts=set(); missing=set(); outside=[]
    inactive=set()
    for ax in fig.axes:
        for axis in [ax.xaxis, ax.yaxis]:
            lo,hi=sorted(axis.get_view_interval())
            for tick in axis.get_major_ticks()+axis.get_minor_ticks():
                if not lo-1e-9 <= tick.get_loc() <= hi+1e-9:
                    inactive.update([id(tick.label1),id(tick.label2)])
    # 選択されたフォントを実名で検査。各Textの字形がフォントに収録されているかも確認。
    for item in fig.findobj(Text):
        if id(item) in inactive or not item.get_visible() or not item.get_text(): continue
        fp=font_manager.findfont(item.get_fontproperties())
        ft=ft2font.FT2Font(fp); fonts.add(ft.family_name); cmap=ft.get_charmap()
        for char in item.get_text():
            if not char.isspace() and ord(char) not in cmap: missing.add(char)
        bb=item.get_window_extent(renderer)
        if bb.width>0 and (bb.x0 < -1 or bb.y0 < -1 or bb.x1 > 1601 or bb.y1 > 901):
            outside.append(item.get_text())
    assert not missing, f'未収録字形: {sorted(missing)}'
    assert not outside, f'画像外の文字: {outside}'
    name=f'chart_{index:02d}_{NAMES[index-1]}.png'; output=OUT/name
    fig.savefig(output,dpi=200)  # bbox_inches=tightは画素数を変えるため使わない。
    with Image.open(output) as im:
        assert im.size==(1600,900), (name,im.size)
        assert im.getpixel((0,0))[:3]==(250,249,245)
    record={'file':name,'pixels':[1600,900],'fonts':sorted(fonts),'missing_glyphs':[],
      'text_outside_canvas':[],'bytes':output.stat().st_size}
    print(json.dumps(record,ensure_ascii=False)); plt.close(fig)
    return record

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--only',type=int,choices=range(1,14),help='指定した図番号だけ再生成（例:03）')
    args=parser.parse_args(); OUT.mkdir(parents=True,exist_ok=True); QA.mkdir(parents=True,exist_ok=True)
    verify_physics()
    print(f'Python {sys.version.split()[0]} / matplotlib {matplotlib.__version__} / numpy {np.__version__}')
    fontpath=font_manager.findfont(font_manager.FontProperties(family=plt.rcParams['font.family']))
    print('選択フォント: '+font_manager.FontProperties(fname=fontpath).get_name())
    records=[]
    for index in ([args.only] if args.only else range(1,14)):
        records.append(save_checked(globals()[f'chart_{index:02d}'](),index))
    manifest=QA/'chart_validation.json'
    if args.only and manifest.exists():
        old=json.loads(manifest.read_text(encoding='utf-8'))['figures']
        records=sorted([r for r in old if r['file']!=records[0]['file']]+records,key=lambda r:r['file'])
    manifest.write_text(json.dumps({'python':sys.version.split()[0],'matplotlib':matplotlib.__version__,
      'numpy':np.__version__,'physics_checks':'passed','figures':records},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

if __name__=='__main__':
    main()
