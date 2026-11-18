import csv, json, re, os
from datetime import datetime
from collections import defaultdict

def parse_val(v):
    if not v: return 0.0
    v = str(v).replace('.', '').replace(',', '.')
    try: return float(v)
    except: return 0.0

def parse_qty(q):
    if not q: return 0.0
    q = str(q).strip().replace('.', '').replace(',', '.')
    if q in ['#N/D', '#N/A', '-', '']: return 0.0
    try: return float(q)
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

def categorize_item(fam, desc, gl_name, group2=''):
    d = (str(desc or '') + ' ' + str(gl_name or '') + ' ' + str(group2 or '')).lower()
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

# 1. Carregar Dados de 2026
file_2026 = 'dados/2026 com quantidade e codigo do material.csv'
print(f"1. Carregando dados de 2026 a partir de '{file_2026}'...")
records_2026 = []

with open(file_2026, 'r', encoding='latin1') as f:
    r = csv.reader(f, delimiter=';')
    header = next(r)
    # Indices detectados em 2026:
    # 0: Data, 1: Group, 2: Account, 3: General Ledger Account, 4: Item, 5: Note, 6: History,
    # 7: Value, 8: Supplier, 9: Descrição, 10: Classification in YTW, 11: ID SD3,
    # 12: Semana SD3, 13: Mes SD3, 14: |Valor|, 15: QTY, 16: Code, 17: Description SD3,
    # 18: Materal/service, 19: Group2, 20: Family
    for row in r:
        if not row or len(row) < 8: continue
        d_str = row[0].strip()
        v = parse_val(row[7])
        qty = parse_qty(row[15]) if len(row) > 15 else 0.0
        code = row[16].strip() if len(row) > 16 else ''
        if code in ['#N/D', '#N/A', '-']: code = ''
        desc_sd3 = row[17].strip() if len(row) > 17 and row[17].strip() not in ['#N/D', ''] else ''
        mat_serv = row[18].strip() if len(row) > 18 and row[18].strip() not in ['#N/D', ''] else ''
        group2 = row[19].strip() if len(row) > 19 and row[19].strip() not in ['#N/D', ''] else ''
        fam_detail = row[20].strip() if len(row) > 20 and row[20].strip() not in ['#N/D', ''] else ''
        
        # Semana SD3
        wk = 0
        if len(row) > 12 and row[12].strip().isdigit():
            wk = int(row[12].strip())
        else:
            try:
                dt = datetime.strptime(d_str, '%d/%m/%Y')
                wk = dt.isocalendar()[1]
            except:
                wk = 0
                
        try:
            dt = datetime.strptime(d_str, '%d/%m/%Y')
            iso_d = dt.strftime('%Y-%m-%d')
        except:
            iso_d = d_str
            
        grp = row[1].strip() if len(row) > 1 else ''
        acct = row[2].strip() if len(row) > 2 else ''
        gl_name = row[3].strip() if len(row) > 3 else ''
        mach_item = row[4].strip() if len(row) > 4 else ''
        note = row[5].strip() if len(row) > 5 else ''
        hist = row[6].strip() if len(row) > 6 else ''
        sup = row[8].strip() if len(row) > 8 else ''
        desc_raw = row[9].strip() if len(row) > 9 else ''
        
        fam = get_family(acct)
        is_service = (mat_serv.lower() == 'services') or ('service' in acct.lower()) or ('serviço' in desc_raw.lower())
        
        display_desc = desc_sd3 if desc_sd3 else (desc_raw if desc_raw else gl_name)
        
        records_2026.append({
            'date': iso_d,
            'week': wk,
            'group': grp,
            'account': acct,
            'family': fam,
            'gl_name': gl_name,
            'item': mach_item,
            'note': note,
            'hist': hist,
            'value': v,
            'qty': qty,
            'code': code,
            'desc_sd3': desc_sd3,
            'mat_serv': mat_serv,
            'group2': group2,
            'fam_detail': fam_detail,
            'sup': sup,
            'desc': display_desc,
            'is_service': is_service
        })

print(f"Carregados {len(records_2026)} registros para 2026.")

# 2. Carregar Dados de 2025
file_2025 = 'dados/2025 com quantidade e codigo do material.csv'
print(f"2. Carregando dados de 2025 a partir de '{file_2025}'...")
records_2025 = []

with open(file_2025, 'r', encoding='latin1') as f:
    r = csv.reader(f, delimiter=';')
    header = next(r)
    # Indices detectados em 2025:
    # 0: Data, 1: Group, 2: Account, 3: General Ledger Account, 4: Item, 5: Note, 6: History,
    # 7: Description, 8: Value, 9: Supplier, 10: Classification in YTW, 11: Semana SD3,
    # 12: Mes SD3, 13: |Valor|, 14: Code, 15: Description SD3, 16: Material/service, 17: Family, 18: QTY
    for row in r:
        if not row or len(row) < 9: continue
        d_str = row[0].strip()
        v = parse_val(row[8])
        qty = parse_qty(row[18]) if len(row) > 18 else 0.0
        code = row[14].strip() if len(row) > 14 else ''
        if code in ['#N/D', '#N/A', '-']: code = ''
        desc_sd3 = row[15].strip() if len(row) > 15 and row[15].strip() not in ['#N/D', ''] else ''
        mat_serv = row[16].strip() if len(row) > 16 and row[16].strip() not in ['#N/D', ''] else ''
        fam_detail = row[17].strip() if len(row) > 17 and row[17].strip() not in ['#N/D', ''] else ''
        
        wk = 0
        if len(row) > 11 and row[11].strip().isdigit():
            wk = int(row[11].strip())
        else:
            try:
                dt = datetime.strptime(d_str, '%d/%m/%Y')
                wk = dt.isocalendar()[1]
            except:
                wk = 0
                
        try:
            dt = datetime.strptime(d_str, '%d/%m/%Y')
            iso_d = dt.strftime('%Y-%m-%d')
        except:
            iso_d = d_str
            
        grp = row[1].strip() if len(row) > 1 else ''
        acct = row[2].strip() if len(row) > 2 else ''
        gl_name = row[3].strip() if len(row) > 3 else ''
        mach_item = row[4].strip() if len(row) > 4 else ''
        desc_raw = row[7].strip() if len(row) > 7 else ''
        sup = row[9].strip() if len(row) > 9 else ''
        
        display_desc = desc_sd3 if desc_sd3 else (desc_raw if desc_raw else gl_name)
        
        records_2025.append({
            'date': iso_d,
            'week': wk,
            'group': grp,
            'account': acct,
            'family': get_family(acct),
            'item': mach_item,
            'value': v,
            'qty': qty,
            'code': code,
            'desc_sd3': desc_sd3,
            'mat_serv': mat_serv,
            'fam_detail': fam_detail,
            'sup': sup,
            'desc': display_desc
        })

print(f"Carregados {len(records_2025)} registros para 2025.")

# 3. Metas Oficiais de Orçamento e Diagnóstico Executivo para WK 44
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

# 4. Dados Oficiais da Curva S (PowerPoint WK 44)
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

# 5. Análise de Inflexão na WK 22 por Família
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

# 6. Inteligência Semanal por Frota (W01 a W45)
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

max_wk_2026 = max(x['week'] for x in records_2026 if x['week'] > 0)
print(f"Semanas ativas detectadas em 2026: 1 a {max_wk_2026}")

frotas_analytics = {}

for f in fleet_list:
    semanas = {}
    for w in range(1, max_wk_2026 + 1):
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
    mach_items_pre = defaultdict(lambda: defaultdict(lambda: [0.0, 0.0])) # [qty, val]
    mach_items_post = defaultdict(lambda: defaultdict(lambda: [0.0, 0.0]))
    cat_pre = defaultdict(float)
    cat_post = defaultdict(float)
    cat_tot = defaultdict(float)

    for x in records_2026:
        if x['family'] != f or x['week'] < 1 or x['week'] > max_wk_2026: continue
        w = x['week']
        v = x['value']
        q = x['qty'] if x['qty'] > 0 else 1.0
        desc = clean_desc(x['desc'] or x['gl_name'])
        cat = categorize_item(f, x['desc'], x['gl_name'], x['group2'])
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
                mach_items_pre[mach_name][desc][0] += q
                mach_items_pre[mach_name][desc][1] += v
        else:
            maquinas[mach_name]['post'] += v
            cat_post[cat] += v
            if desc and v > 0:
                mach_items_post[mach_name][desc][0] += q
                mach_items_post[mach_name][desc][1] += v
        cat_tot[cat] += v
        
        if v > maquinas[mach_name]['top_val']:
            maquinas[mach_name]['top_val'] = v
            maquinas[mach_name]['top_item'] = desc

    semanas_list = []
    for w in range(1, max_wk_2026 + 1):
        item_w = semanas[w]
        semanas_list.append({
            'week': w,
            'total': item_w['total'],
            'is_pos_wk22': item_w['is_pos_wk22'],
            'top_item': item_w['top_item'],
            'top_val': item_w['top_val'],
            'top_mach': item_w['top_mach'],
            'categorias': dict(item_w['categorias'])
        })

    pre_tot_f = sum(s['total'] for s in semanas_list if s['week'] < 22)
    post_tot_f = sum(s['total'] for s in semanas_list if s['week'] >= 22)
    num_post_weeks = max_wk_2026 - 21

    all_cats = list(cat_tot.keys())
    cat_comp = []
    for c in all_cats:
        pre_c = cat_pre[c]
        post_c = cat_post[c]
        pre_m = pre_c / 21 if pre_c > 0 else 0
        post_m = post_c / num_post_weeks if post_c > 0 else 0
        aum_pct = (((post_m / pre_m) - 1) * 100) if pre_m > 0 else (100.0 if post_c > 0 else 0.0)
        cat_comp.append({
            'categoria': c,
            'pre': pre_c,
            'post': post_c,
            'pre_total': pre_c,
            'post_total': post_c,
            'total': cat_tot[c],
            'share': (cat_tot[c] / sum(cat_tot.values()) * 100) if sum(cat_tot.values()) > 0 else 0,
            'aumento_pct': round(aum_pct, 1)
        })
    cat_comp.sort(key=lambda t: t['total'], reverse=True)

    mach_ranking = []
    for m, d in maquinas.items():
        pre_items = sorted(mach_items_pre[m].items(), key=lambda t: t[1][1], reverse=True)[:3]
        post_items = sorted(mach_items_post[m].items(), key=lambda t: t[1][1], reverse=True)[:3]
        
        top_pre = [{'nome': k, 'desc': k, 'qtd': int(round(v[0])) if v[0] > 0 else 1, 'count': int(round(v[0])), 'val': v[1]} for k, v in pre_items]
        top_post = [{'nome': k, 'desc': k, 'qtd': int(round(v[0])) if v[0] > 0 else 1, 'count': int(round(v[0])), 'val': v[1]} for k, v in post_items]
        
        mach_ranking.append({
            'maquina': m,
            'pre': d['pre'],
            'post': d['post'],
            'pre_total': d['pre'],
            'post_total': d['post'],
            'total': d['total'],
            'top_item': d['top_item'],
            'top_val': d['top_val'],
            'top_pre': top_pre,
            'top_post': top_post
        })
    mach_ranking.sort(key=lambda t: t['total'], reverse=True)

    frotas_analytics[f] = {
        'info': fleet_meta_info[f],
        'semanas': semanas_list,
        'categorias_comparativo': cat_comp,
        'maquinas_ranking': mach_ranking[:25],
        'pre_total': pre_tot_f,
        'post_total': post_tot_f,
        'pre_media_sem': pre_tot_f / 21 if pre_tot_f > 0 else 0,
        'post_media_sem': post_tot_f / num_post_weeks if post_tot_f > 0 else 0,
        'aumento_pct': (((post_tot_f / num_post_weeks) / (pre_tot_f / 21) - 1) * 100) if pre_tot_f > 0 else 100.0
    }

print("Inteligência semanal de frotas calculada com sucesso!")

# 7. Comparativo 2025 vs 2026 Inteligente (Usando Code e QTY Real)
items_2025 = defaultdict(lambda: {'val': 0.0, 'qty': 0.0, 'count': 0, 'code': '', 'desc': '', 'family': '', 'sup': set()})
for x in records_2025:
    code = x['code']
    desc = clean_desc(x['desc'])
    key = ('CODE:' + code) if code else ('DESC:' + desc)
    if not key or key in ['CODE:', 'DESC:']: continue
    
    items_2025[key]['val'] += x['value']
    items_2025[key]['qty'] += x['qty']
    items_2025[key]['count'] += 1
    if code: items_2025[key]['code'] = code
    if desc and not items_2025[key]['desc']: items_2025[key]['desc'] = desc
    if x['family'] and not items_2025[key]['family']: items_2025[key]['family'] = x['family']
    if x['sup']: items_2025[key]['sup'].add(x['sup'])

items_2026 = defaultdict(lambda: {'val': 0.0, 'qty': 0.0, 'count': 0, 'code': '', 'desc': '', 'family': '', 'group2': '', 'sup': set()})
for x in records_2026:
    code = x['code']
    desc = clean_desc(x['desc'])
    key = ('CODE:' + code) if code else ('DESC:' + desc)
    if not key or key in ['CODE:', 'DESC:']: continue
    
    items_2026[key]['val'] += x['value']
    items_2026[key]['qty'] += x['qty']
    items_2026[key]['count'] += 1
    if code: items_2026[key]['code'] = code
    if desc and not items_2026[key]['desc']: items_2026[key]['desc'] = desc
    if x['family'] and not items_2026[key]['family']: items_2026[key]['family'] = x['family']
    if x['group2'] and not items_2026[key]['group2']: items_2026[key]['group2'] = x['group2']
    if x['sup']: items_2026[key]['sup'].add(x['sup'])

common_keys = set(items_2025.keys()) & set(items_2026.keys())
only_2026_keys = set(items_2026.keys()) - set(items_2025.keys())
only_2025_keys = set(items_2025.keys()) - set(items_2026.keys())

itens_inflacao = []
for k in common_keys:
    d25 = items_2025[k]
    d26 = items_2026[k]
    
    q25 = d25['qty'] if d25['qty'] > 0 else float(d25['count'])
    q26 = d26['qty'] if d26['qty'] > 0 else float(d26['count'])
    
    p25 = d25['val'] / q25 if q25 > 0 else 0.0
    p26 = d26['val'] / q26 if q26 > 0 else 0.0
    
    diff_p = p26 - p25
    diff_pct = (diff_p / p25 * 100) if p25 > 0 else 0.0
    impact_p = diff_p * q26
    impact_v = (q26 - q25) * p25
    
    display_code = d26['code'] or d25['code'] or '-'
    display_desc = d26['desc'] or d25['desc']
    
    itens_inflacao.append({
        'code': display_code,
        'desc': display_desc,
        'family': d26['family'] or d25['family'],
        'group2': d26['group2'] or 'Geral',
        'sup': ", ".join(list(d26['sup'])[:2]),
        'preco_2025': p25,
        'preco_2026': p26,
        'var_preco_pct': diff_pct,
        'qtd_2025': round(q25, 2),
        'qtd_2026': round(q26, 2),
        'var_qtd': round(q26 - q25, 2),
        'impacto_preco': impact_p,
        'impacto_volume': impact_v,
        'total_2026': d26['val']
    })

itens_inflacao.sort(key=lambda t: t['impacto_preco'], reverse=True)

novos_itens_2026 = []
for k in only_2026_keys:
    d = items_2026[k]
    q = d['qty'] if d['qty'] > 0 else float(d['count'])
    novos_itens_2026.append({
        'code': d['code'] or '-',
        'desc': d['desc'],
        'family': d['family'],
        'group2': d['group2'] or 'Geral',
        'sup': ", ".join(list(d['sup'])[:2]),
        'total_val': d['val'],
        'count': d['count'],
        'qty': round(q, 2),
        'preco_medio': d['val'] / q if q > 0 else 0.0
    })
novos_itens_2026.sort(key=lambda t: t['total_val'], reverse=True)

itens_apenas_2025 = []
for k in only_2025_keys:
    d = items_2025[k]
    q = d['qty'] if d['qty'] > 0 else float(d['count'])
    itens_apenas_2025.append({
        'code': d['code'] or '-',
        'desc': d['desc'],
        'family': d['family'],
        'sup': ", ".join(list(d['sup'])[:2]),
        'total_val': d['val'],
        'count': d['count'],
        'qty': round(q, 2),
        'preco_medio': d['val'] / q if q > 0 else 0.0
    })
itens_apenas_2025.sort(key=lambda t: t['total_val'], reverse=True)

# 8. Transações Compactas para Visualização e Tabela Dinâmica
transacoes_compactas = []
for x in records_2026:
    if x['family'] == 'Personnel/Other': continue
    u_price = round(x['value'] / x['qty'], 2) if x['qty'] > 0 else round(x['value'], 2)
    transacoes_compactas.append({
        'd': x['date'],
        'w': x['week'],
        'f': x['family'],
        'a': x['account'],
        'i': x['item'],
        's': x['sup'],
        'v': round(x['value'], 2),
        'q': round(x['qty'], 2) if x['qty'] != 0 else 1,
        'c': x['code'] if x['code'] else '-',
        'u': u_price,
        'g': x['group2'] if x['group2'] else '-',
        't': 'Materials' if not x['is_service'] else 'Services',
        'm': x['desc'],
        'h': x['hist'][:120] if x['hist'] else ''
    })

print(f"Geradas {len(transacoes_compactas)} transações compactas.")

# 9. Montar Pacote Consolidado DASHBOARD_DATA
dashboard_bundle = {
    'meta': {
        'titulo': 'Dashboard de Custos de Manutenção & Frotas - TCP',
        'subtitulo': f'Terminal de Contêineres de Paranaguá :: Gestão Orçamentária 2025 vs 2026 :: Week {max_wk_2026}',
        'budget_total': 30776307.69,
        'real_total': 40533493.23,
        'balance_total': -9757185.54,
        'balance_total_pct': -31.70,
        'media_semanal': 908825.42,
        'forecast_anual': 47258921.68,
        'max_week': max_wk_2026,
        'total_itens_comuns': len(common_keys),
        'total_novos_itens_2026': len(only_2026_keys),
        'gasto_novos_itens_2026': sum(x['total_val'] for x in novos_itens_2026),
        'total_itens_apenas_2025': len(only_2025_keys),
        'gasto_apenas_2025': sum(x['total_val'] for x in itens_apenas_2025),
        'data_atualizacao': 'Novembro 2026 (Base Oficial com Code e QTY)'
    },
    'curva_s': curva_s,
    'familias': familias_oficiais,
    'wk22_comparativo': wk22_comparativo_familias,
    'frotas_analytics': frotas_analytics,
    'rtg_analytics': frotas_analytics['RTG'],
    'itens_inflacao_top': itens_inflacao,
    'novos_itens_top': novos_itens_2026,
    'itens_apenas_2025_top': itens_apenas_2025,
    'transacoes': transacoes_compactas
}

with open('dashboard_data.js', 'w', encoding='utf-8') as f:
    f.write("// TCP Maintenance Cost Intelligence Data Bundle (Atualizado com Code & QTY)\n")
    f.write("window.DASHBOARD_DATA = ")
    json.dump(dashboard_bundle, f, ensure_ascii=False)
    f.write(";\n")

print("Sucesso! 'dashboard_data.js' gerado com sucesso a partir das bases novas de 2025 e 2026!")
