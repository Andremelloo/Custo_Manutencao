import openpyxl, csv, json, re
from datetime import datetime
from collections import defaultdict

def parse_val(v):
    if not v: return 0.0
    v = str(v).replace('.', '').replace(',', '.')
    try: return float(v)
    except: return 0.0

def clean_desc(d):
    d = str(d or '').strip().upper()
    d = re.sub(r'\s+', ' ', d)
    return d

def get_family(account):
    a = str(account or '').lower()
    if 'rtg' in a or 'transteiner' in a: return 'RTG'
    if 'tt' in a or 'terminals' in a: return 'TT'
    if 'sts' in a or 'portainer' in a: return 'STS'
    if 'reach stacker' in a: return 'RS'
    if 'empty forklift' in a: return 'EH'
    if 'mobile crane' in a: return 'MHC'
    if 'truck' in a: return 'Trucks'
    if 'warehouse forklift' in a: return 'WHF'
    if 'bus' in a: return 'Bus'
    if 'asset disposal' in a: return 'Asset Disposal'
    if any(k in a for k in ['machine', 'tool', 'building', 'car', 'freight', 'road fee', 'office', 'it material', 'kitchen', 'property rental']):
        return 'Others'
    return 'Personnel/Other'

def format_machine_code(fam, code):
    c = str(code or '').strip()
    if not c: return 'Frota Geral / Estoque'
    if fam == 'RTG' and len(c) == 3 and c.startswith('7'): return f'RTG#{c[1:]}'
    if fam == 'STS' and len(c) == 3 and c.startswith('9'): return f'STS#{c[1:]}'
    if fam == 'RS' and len(c) == 3 and c.startswith('5'): return f'RS#{c[1:]}'
    if fam == 'EH' and len(c) == 3 and c.startswith('4'): return f'EH#{c[1:]}'
    if fam == 'MHC' and c in ['950', '951']: return f'MHC#{int(c)-949:02d}'
    if fam == 'TT' and len(c) == 3 and c.startswith('3'): return f'TT#{c[1:]}'
    return f'{fam} {c}'

def categorize_item(fam, desc, gl_name):
    d = (str(desc or '') + ' ' + str(gl_name or '')).lower()
    if fam == 'RTG':
        if any(k in d for k in ['freio', 'brake', 'tr-11', 'sapata']): return 'Freios (Gantry/Trolley)'
        if any(k in d for k in ['gerador', 'alternador', 'generator']): return 'Geradores & Alternadores'
        if any(k in d for k in ['esteira', 'cabletrack', 'cable track', 'brevetti']): return 'Esteiras (Cabletrack)'
        if any(k in d for k in ['bomba', 'injetor', 'combustivel', 'bico']): return 'Injeção & Combustível'
        if any(k in d for k in ['motor', 'mfxp', 'scania', 'ventilad']): return 'Motores & Acionamentos'
        if any(k in d for k in ['cabo', 'eletric', 'inversor', 'fusivel', 'sensor', 'modulo', 'siemens', 'contator', 'rele', 'placa']): return 'Elétrica & Automação'
        return 'Outros RTG'
    elif fam == 'TT':
        if any(k in d for k in ['pneu', 'caminh', '310/80', 'michelin', 'roda']): return 'Pneus & Rodas'
        if any(k in d for k in ['eixo', 'tandem', 'carreta', 'ch ', 'ch-', 'truque']): return 'Eixos Tandem & Carretas'
        if any(k in d for k in ['freio', 'sapata', 'tambor', 'pastilha', 'cuica']): return 'Freios & Sapatas'
        if any(k in d for k in ['diferencial', 'transmiss', 'cardan', 'embreag', 'cambio']): return 'Transmissão & Diferencial'
        if any(k in d for k in ['motor', 'scania', 'cummins', 'radiad', 'turbina', 'bloco']): return 'Motor Diesel & Arrefecimento'
        if any(k in d for k in ['oleo', 'lubrif', 'filtro', 'graxa', 'hidraul']): return 'Lubrificantes & Filtros'
        return 'Outros TT'
    elif fam == 'STS':
        if any(k in d for k in ['cabo', 'bridon', 'iph', 'elevac', 'aco']): return 'Cabos de Aço (Elevação)'
        if any(k in d for k in ['freio', 'sb28', 'bint', 'disco', 'sapata']): return 'Freios (Elevação & Translação)'
        if any(k in d for k in ['inversor', 'danfoss', 'modulo', 'siemens', 'plc', 'sensor', 'eletric']): return 'Elétrica & Inversores'
        if any(k in d for k in ['spreader', 'bromma', 'twistlock', 'trava', 'polia']): return 'Spreaders & Peças'
        if any(k in d for k in ['oleo', 'lubrif', 'redutor', 'filtro', 'graxa']): return 'Lubrificantes & Redutores'
        return 'Outros STS'
    elif fam == 'RS':
        if any(k in d for k in ['bomba', 'hidraul', 'valvula', 'cilindro', 'mangueira']): return 'Sistema Hidráulico & Bombas'
        if any(k in d for k in ['roda', 'cubo', 'pneu', 'aro']): return 'Rodas, Pneus & Cubos'
        if any(k in d for k in ['transmiss', 'dana', 'clark', 'conversor', 'eixo', 'cardan']): return 'Transmissão & Eixos'
        if any(k in d for k in ['spreader', 'twistlock', 'trava', 'cabecote', 'lanca']): return 'Spreader & Lança'
        if any(k in d for k in ['motor', 'scania', 'volvo', 'radiad', 'filtro', 'oleo', 'lubrif']): return 'Motor, Lubrificantes & Filtros'
        return 'Outros RS'
    elif fam == 'EH':
        if any(k in d for k in ['garfo', 'suporte', 'mastro', 'torre']): return 'Garfos & Mastro'
        if any(k in d for k in ['pneu', 'roda', 'aro', '140024']): return 'Pneus & Rodas'
        if any(k in d for k in ['transmiss', 'conversor', 'modulo']): return 'Transmissão & Módulos'
        if any(k in d for k in ['cilindro', 'inclinac', 'elevac', 'valvula', 'hidraul']): return 'Cilindros & Hidráulica'
        if any(k in d for k in ['spreader', 'twistlock', 'controle', 'fl#01']): return 'Spreader & Controles'
        return 'Outros EH'
    elif fam == 'MHC':
        if any(k in d for k in ['bomba', 'hidraul', 'motor hidraul']): return 'Bombas & Hidráulica Principal'
        if any(k in d for k in ['manga', 'eixo', 'rolamento', 'luva']): return 'Manga & Eixos'
        if any(k in d for k in ['cabo', 'cabo de aco', 'guincho', 'polia']): return 'Cabos & Guinchos'
        if any(k in d for k in ['oleo', 'lubrif', 'atf', 'filtro']): return 'Lubrificantes & Fluidos'
        return 'Outros MHC'
    return 'Geral'

print("1. Loading 2026 data from 2026.csv...")
records_2026 = []
with open('2026.csv', 'r', encoding='latin1') as f:
    r = csv.reader(f, delimiter=';')
    for _ in range(4): next(r)
    for row in r:
        if not row or len(row) < 9: continue
        d_str = row[0].strip()
        v = parse_val(row[8])
        try:
            dt = datetime.strptime(d_str, '%d/%m/%Y')
            wk = dt.isocalendar()[1]
            iso_d = dt.strftime('%Y-%m-%d')
        except:
            wk = 0
            iso_d = d_str
            
        grp = row[1].strip() if len(row) > 1 else ''
        acct = row[2].strip() if len(row) > 2 else ''
        gl_id = row[3].strip() if len(row) > 3 else ''
        gl_name = row[4].strip() if len(row) > 4 else ''
        item = row[5].strip() if len(row) > 5 else ''
        note = row[6].strip() if len(row) > 6 else ''
        hist = row[7].strip() if len(row) > 7 else ''
        sup = row[9].strip() if len(row) > 9 else ''
        desc = row[10].strip() if len(row) > 10 else ''
        fam = get_family(acct)
        is_service = 'service' in acct.lower() or 'sm ' in gl_name.lower() or 'serviço' in desc.lower()
        
        records_2026.append({
            'date': iso_d,
            'week': wk,
            'group': grp,
            'account': acct,
            'family': fam,
            'gl_name': gl_name,
            'item': item,
            'note': note,
            'hist': hist,
            'value': v,
            'sup': sup,
            'desc': desc,
            'is_service': is_service
        })

print(f"Loaded {len(records_2026)} records for 2026.")

print("2. Loading 2025 data from 2025.xlsx...")
wb = openpyxl.load_workbook('2025.xlsx', data_only=True)
ws = wb.active
records_2025 = []
for r in range(4, ws.max_row + 1):
    d = ws.cell(r, 1).value
    acct = str(ws.cell(r, 4).value or '').strip()
    val = ws.cell(r, 13).value
    sup = str(ws.cell(r, 14).value or '').strip()
    desc = str(ws.cell(r, 15).value or '').strip()
    item = str(ws.cell(r, 10).value or '').strip()
    
    if val is not None:
        try: vf = float(val)
        except: continue
        dt_str = d.strftime('%Y-%m-%d') if hasattr(d, 'strftime') else str(d)[:10]
        wk = d.isocalendar()[1] if hasattr(d, 'isocalendar') else 0
        records_2025.append({
            'date': dt_str,
            'week': wk,
            'account': acct,
            'family': get_family(acct),
            'item': item,
            'value': vf,
            'sup': sup,
            'desc': desc
        })

print(f"Loaded {len(records_2025)} records for 2025.")

# 3. Official Slide / Budget Data for WK 44
familias_oficiais = [
    {
        'account': 'STS',
        'nome': 'STS (Ship-to-Shore Cranes)',
        'budget': 2772846.15,
        'accum_cost': 3628550.85,
        'balance': -855704.70,
        'balance_pct': -30.86,
        'notes': 'Troca de cabos de elevação nos STS#08, #07 e #11 (R$ 725.725); Troca de freios de elevação no STS#09 e #10 (R$ 188.926); Reparo emergencial no cabo de média tensão STS#09 após esmagamento acidental (R$ 39.000).'
    },
    {
        'account': 'RTG',
        'nome': 'RTG (Rubber Tyred Gantry)',
        'budget': 12998615.38,
        'accum_cost': 15360228.76,
        'balance': -2361613.38,
        'balance_pct': -18.17,
        'notes': '132 freios de gantry/translado (R$ 979.849); 13 geradores substituídos (R$ 467.241); 73 motores de trolley/auxiliares (R$ 543.829); 56 freios de trolley/aux (R$ 226.208); Esteiras porta-cabos Brevetti nos RTG#17 e #15 (R$ 214.165); Bomba injetora de diesel do RTG#38 (R$ 189.566); Bicos injetores RTG#16 (R$ 60.485).'
    },
    {
        'account': 'TT',
        'nome': 'TT (Terminal Tractors)',
        'budget': 6969769.23,
        'accum_cost': 10770689.99,
        'balance': -3800920.76,
        'balance_pct': -54.53,
        'notes': '967 pneus consumidos (R$ 1.692.183); Reformas e substituições de eixos tandem de carretas CH (R$ 1.243.899); Substituição de 192 sapatas de freio CH (R$ 606.766); Reparos em diferenciais de TT (R$ 223.691); Troca do motor diesel do TT#30 (R$ 89.036).'
    },
    {
        'account': 'RS',
        'nome': 'RS (Reach Stackers)',
        'budget': 2659461.54,
        'accum_cost': 3227444.01,
        'balance': -567982.47,
        'balance_pct': -21.36,
        'notes': 'Substituição e reparo de 12 bombas hidráulicas (R$ 193.395); Troca de 10 cubos de roda/rodas (R$ 119.593).'
    },
    {
        'account': 'EH',
        'nome': 'EH (Empty Handlers / Empilhadeiras Vazio)',
        'budget': 1012846.15,
        'accum_cost': 1235933.50,
        'balance': -223087.35,
        'balance_pct': -22.03,
        'notes': 'Suporte de garfo da FL#01 (R$ 95.287); Módulo de transmissão EH#04 (R$ 43.903); Unidade de controle do spreader EH#06 (R$ 37.078); Troca do cilindro de inclinação da torre EH#05 (R$ 22.687); Partes de transmissão EH (R$ 21.596); Cilindro de elevação EH#04 (R$ 9.790).'
    },
    {
        'account': 'MHC',
        'nome': 'MHC (Mobile Harbour Cranes)',
        'budget': 368076.92,
        'accum_cost': 775660.19,
        'balance': -407583.27,
        'balance_pct': -110.73,
        'notes': 'Reparo da bomba hidráulica principal do MHC#01 (R$ 231.375); Reparo da bomba hidráulica tripla do MHC#02 (R$ 73.400); Substituição da luva de eixo do MHC#01 (R$ 44.531).'
    },
    {
        'account': 'WHF',
        'nome': 'WHF (Warehouse Forklifts / Empilhadeiras Armazém)',
        'budget': 265692.31,
        'accum_cost': 226622.58,
        'balance': 39069.73,
        'balance_pct': 14.70,
        'notes': 'Operação dentro do orçamento com economia de R$ 39k (+14,7%). Manutenções preventivas regulares e baixo índice de corretivas graves.'
    },
    {
        'account': 'Trucks',
        'nome': 'Trucks (Caminhões de Apoio)',
        'budget': 335923.08,
        'accum_cost': 307796.12,
        'balance': 28126.96,
        'balance_pct': 8.37,
        'notes': 'Operação dentro do orçamento com economia de R$ 28k (+8,4%). Manutenção controlada da frota de utilitários.'
    },
    {
        'account': 'Bus',
        'nome': 'Bus (Ônibus e Vans de Transporte)',
        'budget': 84615.38,
        'accum_cost': 169742.67,
        'balance': -85127.29,
        'balance_pct': -100.60,
        'notes': 'Reparo estrutural no Bus#01 (R$ 31.721); Reparo do ar condicionado do Bus#03 (R$ 22.293); Substituição do sistema contra incêndio do Ônibus Elétrico 03 (R$ 8.889); Troca de vidros Bus#03 (R$ 9.100).'
    },
    {
        'account': 'Asset Disposal',
        'nome': 'Asset Disposal (Descarte de Ativos)',
        'budget': 1914000.00,
        'accum_cost': 3086878.42,
        'balance': -1172878.42,
        'balance_pct': -61.28,
        'notes': 'Baixas contábeis e descarte de ativos não orçados ou com valor residual superior ao planejado, com concentração expressiva a partir da Semana 35.'
    },
    {
        'account': 'Others',
        'nome': 'Outros Serviços & Instalações',
        'budget': 1394461.54,
        'accum_cost': 1743946.14,
        'balance': -349484.60,
        'balance_pct': -25.06,
        'notes': 'Adequação e serviços corretivos de compressores conforme norma NR-12 (R$ 93.000); Inspeção e ajuste normativo de pontes rolantes da oficina, STS e SE-00 pela Grams (R$ 148.000); Certificações de segurança LRQA (R$ 217.335).'
    }
]

# 4. Weekly S-Curve Data from PowerPoint chart39.xml
curva_s_semanas = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 44]
curva_s_forecast = [
    0, 1398923.08, 2797846.15, 4196769.23, 5595692.31, 6994615.38, 8393538.46, 9792461.54,
    11191384.62, 12590307.69, 13989230.77, 15388153.85, 16787076.92, 18186000.00, 19584923.08,
    20983846.15, 22382769.23, 23781692.31, 25180615.38, 26579538.46, 27978461.54, 29377384.62, 30776307.69
]
curva_s_real = [
    0, 905292.92, 2610077.37, 4533243.64, 5584187.08, 6787484.17, 8236234.56, 9716584.09,
    11511893.83, 13120380.56, 15075993.20, 16926179.80, 18987635.40, 20527805.10, 22165097.30,
    23680917.10, 26196216.00, 29583381.20, 31687632.59, 33718213.46, 35822451.92, 37909692.83, 40533493.23
]

curva_s = []
for i in range(len(curva_s_semanas)):
    wk = curva_s_semanas[i]
    f = curva_s_forecast[i]
    r = curva_s_real[i]
    bal = f - r
    bal_pct = ((f - r) / f * 100) if f > 0 else 0
    curva_s.append({
        'week': wk,
        'forecast': f,
        'real': r,
        'balance': bal,
        'balance_pct': bal_pct,
        'is_wk22_point': (wk >= 22)
    })

# 5. WK 22 Deep-Dive Analytics
pre_w22_fam = defaultdict(float)
post_w22_fam = defaultdict(float)
for x in records_2026:
    if x['family'] == 'Personnel/Other': continue
    if x['week'] <= 21:
        pre_w22_fam[x['family']] += x['value']
    elif x['week'] <= 44:
        post_w22_fam[x['family']] += x['value']

familias_nomes = list(set(list(pre_w22_fam.keys()) + list(post_w22_fam.keys())))
wk22_comparativo_familias = []
for f in familias_nomes:
    pre_tot = pre_w22_fam[f]
    post_tot = post_w22_fam[f]
    pre_media = pre_tot / 21
    post_media = post_tot / 23
    crescimento = ((post_media / pre_media - 1) * 100) if pre_media > 0 else 100.0
    wk22_comparativo_familias.append({
        'family': f,
        'pre_total': pre_tot,
        'post_total': post_tot,
        'pre_media_sem': pre_media,
        'post_media_sem': post_media,
        'aumento_pct': crescimento
    })

wk22_comparativo_familias.sort(key=lambda t: t['post_total'], reverse=True)

# =========================================================================
# 6. WEEK-BY-WEEK INTELLIGENCE FOR ALL 6 MAIN FLEETS (W01-W44)
# (RTG, TT, STS, RS, EH, MHC)
# =========================================================================
fleet_list = ['TT', 'STS', 'RS', 'EH', 'MHC', 'RTG']
fleet_meta_info = {
    'TT': {
        'nome': 'TT (Terminal Tractors)',
        'icone': '🚛',
        'budget': 6969769.23,
        'accum_cost': 10770689.99,
        'balance': -3800920.76,
        'balance_pct': -54.53,
        'alert': 'A frota de TT apresentou o maior estouro orçamentário (-R$ 3,80M / -54,53%). O ritmo semanal mais que dobrou (+125,9%), saindo de R$ 147k/sem para R$ 332k/sem devido ao ciclo concentrado de 967 pneus Michelin (R$ 1,69M) e reformas de eixos tandem de carretas CH (R$ 1,24M).'
    },
    'STS': {
        'nome': 'STS (Ship-to-Shore Cranes)',
        'icone': '⚓',
        'budget': 2772846.15,
        'accum_cost': 3628550.85,
        'balance': -855704.70,
        'balance_pct': -30.86,
        'alert': 'A frota de STS acelerou +103,4% após a WK 22 (de R$ 53k/sem para R$ 108k/sem). O estouro de -R$ 855k foi puxado pela troca emergencial e preventiva de cabos de elevação Bridon nos STS#08, #07 e #11 (R$ 725k) e freios SB28 (R$ 189k).'
    },
    'RS': {
        'nome': 'RS (Reach Stackers)',
        'icone': '🚜',
        'budget': 2659461.54,
        'accum_cost': 3227444.01,
        'balance': -567982.47,
        'balance_pct': -21.36,
        'alert': 'As empilhadeiras pesadas RS tiveram salto de +68,8% no ritmo semanal pós-WK22 (de R$ 51k/sem para R$ 86k/sem), totalizando -R$ 568k de desvio devido à troca e reparo de 12 bombas hidráulicas principais (R$ 193k) e 10 cubos de roda/rodas.'
    },
    'EH': {
        'nome': 'EH (Empty Handlers / Vazio)',
        'icone': '📦',
        'budget': 1012846.15,
        'accum_cost': 1235933.50,
        'balance': -223087.35,
        'balance_pct': -22.03,
        'alert': 'A frota de vazios subiu +55,5% na média semanal (de R$ 21,5k/sem para R$ 33,5k/sem), acumulando desvio de -R$ 223k. Destacam-se o suporte de garfo da FL#01 (R$ 95k) e módulos de transmissão e controle do spreader.'
    },
    'MHC': {
        'nome': 'MHC (Mobile Harbour Cranes)',
        'icone': '🏗️',
        'budget': 368076.92,
        'accum_cost': 775660.19,
        'balance': -407583.27,
        'balance_pct': -110.73,
        'alert': 'Os guindastes móveis apresentaram o maior estouro percentual (-110,73%), gastando mais do que o dobro do planejado devido a paradas corretivas severas: reforma da bomba principal do MHC#01 (R$ 231k) e bomba tripla do MHC#02 (R$ 73k).'
    },
    'RTG': {
        'nome': 'RTG (Rubber Tyred Gantry)',
        'icone': '🏗️',
        'budget': 12998615.38,
        'accum_cost': 15360228.76,
        'balance': -2361613.38,
        'balance_pct': -18.17,
        'alert': 'A frota de RTG acelerou +78,5% a partir da WK 22 (de R$ 242k/sem para R$ 431k/sem), resultando em -R$ 2,36M de desvio. Concentração pesada em 132 freios de gantry (R$ 980k), esteiras Brevetti RTG#15/#17 (R$ 214k) e bomba injetora RTG#38 (R$ 189k).'
    }
}

frotas_analytics = {}

for f in fleet_list:
    # 1. Initialize 44 weeks
    semanas = {}
    for w in range(1, 45):
        semanas[w] = {
            'week': w,
            'total': 0.0,
            'is_pos_wk22': (w >= 22),
            'top_item': '',
            'top_val': 0.0,
            'top_mach': '',
            'categorias': defaultdict(float)
        }
    
    maquinas = defaultdict(lambda: {'pre': 0.0, 'post': 0.0, 'total': 0.0, 'top_item': '', 'top_val': 0.0})
    mach_items_pre = defaultdict(lambda: defaultdict(lambda: [0, 0.0]))
    mach_items_post = defaultdict(lambda: defaultdict(lambda: [0, 0.0]))
    cat_pre = defaultdict(float)
    cat_post = defaultdict(float)
    cat_tot = defaultdict(float)

    for x in records_2026:
        if x['family'] != f or x['week'] < 1 or x['week'] > 44: continue
        w = x['week']
        v = x['value']
        desc = clean_desc(x['desc'] or x['gl_name'])
        cat = categorize_item(f, x['desc'], x['gl_name'])
        mach_name = format_machine_code(f, x['item'])
        
        semanas[w]['total'] += v
        semanas[w]['categorias'][cat] += v
        if v > semanas[w]['top_val']:
            semanas[w]['top_val'] = v
            semanas[w]['top_item'] = desc
            semanas[w]['top_mach'] = mach_name
            
        maquinas[mach_name]['total'] += v
        if w < 22:
            maquinas[mach_name]['pre'] += v
            cat_pre[cat] += v
            if desc and v > 0:
                mach_items_pre[mach_name][desc][0] += 1
                mach_items_pre[mach_name][desc][1] += v
        else:
            maquinas[mach_name]['post'] += v
            cat_post[cat] += v
            if desc and v > 0:
                mach_items_post[mach_name][desc][0] += 1
                mach_items_post[mach_name][desc][1] += v
        cat_tot[cat] += v
        
        if v > maquinas[mach_name]['top_val']:
            maquinas[mach_name]['top_val'] = v
            maquinas[mach_name]['top_item'] = desc

    # Convert semanas to list and prepare category dicts
    semanas_list = []
    for w in range(1, 45):
        item_w = semanas[w]
        item_w['categorias'] = dict(item_w['categorias'])
        semanas_list.append(item_w)

    # Categories comparative
    cat_comp = []
    for c, tot in cat_tot.items():
        pre_v = cat_pre[c]
        post_v = cat_post[c]
        pre_m = pre_v / 21
        post_m = post_v / 23
        aum = ((post_m / pre_m - 1) * 100) if pre_m > 0 else 100.0
        cat_comp.append({
            'categoria': c,
            'pre_total': pre_v,
            'post_total': post_v,
            'total': tot,
            'pre_media_sem': pre_m,
            'post_media_sem': post_m,
            'aumento_pct': aum
        })
    cat_comp.sort(key=lambda t: t['total'], reverse=True)

    # Machines ranking with Top 3 items pre and post WK22
    mach_ranking = []
    for m, d in maquinas.items():
        if m.startswith('Frota Geral') and d['total'] < 1000: continue
        
        top_pre_list = sorted(mach_items_pre[m].items(), key=lambda t: t[1][1], reverse=True)[:3]
        top_pre = [{'nome': k, 'qtd': v[0], 'val': v[1]} for k, v in top_pre_list if v[1] > 0]
        
        top_post_list = sorted(mach_items_post[m].items(), key=lambda t: t[1][1], reverse=True)[:3]
        top_post = [{'nome': k, 'qtd': v[0], 'val': v[1]} for k, v in top_post_list if v[1] > 0]

        mach_ranking.append({
            'maquina': m,
            'pre_total': d['pre'],
            'post_total': d['post'],
            'total': d['total'],
            'top_item': d['top_item'],
            'top_pre': top_pre,
            'top_post': top_post
        })
    mach_ranking.sort(key=lambda t: t['total'], reverse=True)

    pre_tot_f = sum(s['total'] for s in semanas_list if s['week'] < 22)
    post_tot_f = sum(s['total'] for s in semanas_list if s['week'] >= 22)

    frotas_analytics[f] = {
        'info': fleet_meta_info[f],
        'semanas': semanas_list,
        'categorias_comparativo': cat_comp,
        'maquinas_ranking': mach_ranking[:25],
        'pre_total': pre_tot_f,
        'post_total': post_tot_f,
        'pre_media_sem': pre_tot_f / 21,
        'post_media_sem': post_tot_f / 23,
        'aumento_pct': (((post_tot_f / 23) / (pre_tot_f / 21) - 1) * 100) if pre_tot_f > 0 else 100.0
    }

print("Generated weekly analytics for all 6 main fleets!")

# 7. Item Comparative Analysis 2025 vs 2026
items_2025 = defaultdict(lambda: {'count': 0, 'total_val': 0.0, 'family': 'Others', 'sup': set()})
for x in records_2025:
    d = clean_desc(x['desc'])
    if d:
        items_2025[d]['count'] += 1
        items_2025[d]['total_val'] += x['value']
        items_2025[d]['family'] = x['family']
        if x['sup']: items_2025[d]['sup'].add(x['sup'])

items_2026 = defaultdict(lambda: {'count': 0, 'total_val': 0.0, 'family': 'Others', 'sup': set(), 'code': ''})
for x in records_2026:
    d = clean_desc(x['desc'])
    if d:
        items_2026[d]['count'] += 1
        items_2026[d]['total_val'] += x['value']
        items_2026[d]['family'] = x['family']
        if x['item']: items_2026[d]['code'] = x['item']
        if x['sup']: items_2026[d]['sup'].add(x['sup'])

common_keys = set(items_2025.keys()) & set(items_2026.keys())
only_2026_keys = set(items_2026.keys()) - set(items_2025.keys())
only_2025_keys = set(items_2025.keys()) - set(items_2026.keys())

itens_inflacao = []
for k in common_keys:
    d25 = items_2025[k]
    d26 = items_2026[k]
    p25 = d25['total_val'] / d25['count'] if d25['count'] else 0
    p26 = d26['total_val'] / d26['count'] if d26['count'] else 0
    diff_p = p26 - p25
    diff_pct = (diff_p / p25 * 100) if p25 > 0 else 0
    impact_p = diff_p * d26['count']
    impact_v = (d26['count'] - d25['count']) * p25
    itens_inflacao.append({
        'desc': k,
        'family': d26['family'],
        'sup': ", ".join(list(d26['sup'])[:2]),
        'preco_2025': p25,
        'preco_2026': p26,
        'var_preco_pct': diff_pct,
        'qtd_2025': d25['count'],
        'qtd_2026': d26['count'],
        'var_qtd': d26['count'] - d25['count'],
        'impacto_preco': impact_p,
        'impacto_volume': impact_v,
        'total_2026': d26['total_val']
    })

itens_inflacao.sort(key=lambda t: t['impacto_preco'], reverse=True)

novos_itens_2026 = []
for k in only_2026_keys:
    d = items_2026[k]
    novos_itens_2026.append({
        'desc': k,
        'family': d['family'],
        'sup': ", ".join(list(d['sup'])[:2]),
        'total_val': d['total_val'],
        'count': d['count'],
        'preco_medio': d['total_val'] / d['count'] if d['count'] else 0
    })
novos_itens_2026.sort(key=lambda t: t['total_val'], reverse=True)

itens_apenas_2025 = []
for k in only_2025_keys:
    d = items_2025[k]
    itens_apenas_2025.append({
        'desc': k,
        'family': d['family'],
        'sup': ", ".join(list(d['sup'])[:2]),
        'total_val': d['total_val'],
        'count': d['count'],
        'preco_medio': d['total_val'] / d['count'] if d['count'] else 0
    })
itens_apenas_2025.sort(key=lambda t: t['total_val'], reverse=True)

# 8. Compact transactions for client-side search & table
transacoes_compactas = []
for x in records_2026:
    if x['family'] == 'Personnel/Other': continue
    if x['week'] <= 44:
        transacoes_compactas.append({
            'd': x['date'],
            'w': x['week'],
            'f': x['family'],
            'a': x['account'],
            'i': x['item'],
            's': x['sup'],
            'v': round(x['value'], 2),
            'm': x['desc'] or x['gl_name'],
            'h': x['hist'][:120] if x['hist'] else ''
        })

print(f"Generated {len(transacoes_compactas)} compact transactions.")

dashboard_bundle = {
    'meta': {
        'titulo': 'Dashboard de Custos de Manutenção & Frotas - TCP',
        'subtitulo': 'Terminal de Contêineres de Paranaguá :: Gestão Orçamentária 2025 vs 2026 :: Week 44',
        'budget_total': 30776307.69,
        'real_total': 40533493.23,
        'balance_total': -9757185.54,
        'balance_total_pct': -31.70,
        'media_semanal': 908825.42,
        'forecast_anual': 47258921.68,
        'total_itens_comuns': len(common_keys),
        'total_novos_itens_2026': len(only_2026_keys),
        'gasto_novos_itens_2026': sum(x['total_val'] for x in novos_itens_2026),
        'total_itens_apenas_2025': len(only_2025_keys),
        'gasto_apenas_2025': sum(x['total_val'] for x in itens_apenas_2025),
        'data_atualizacao': 'Novembro 2026'
    },
    'curva_s': curva_s,
    'familias': familias_oficiais,
    'wk22_comparativo': wk22_comparativo_familias,
    'frotas_analytics': frotas_analytics,
    # Keep rtg_analytics for backward compatibility
    'rtg_analytics': frotas_analytics['RTG'],
    'itens_inflacao_top': itens_inflacao[:100],
    'novos_itens_top': novos_itens_2026[:100],
    'itens_apenas_2025_top': itens_apenas_2025[:100],
    'transacoes': transacoes_compactas
}

with open('dashboard_data.js', 'w', encoding='utf-8') as f:
    f.write("// TCP Maintenance Cost Intelligence Data Bundle\n")
    f.write("window.DASHBOARD_DATA = ")
    json.dump(dashboard_bundle, f, ensure_ascii=False)
    f.write(";\n")

print("Generated dashboard_data.js with all fleets analytics successfully!")
