import os
import time
import argparse
import subprocess
import pandas as pd

start = time.time()
### flags parser
parser = argparse.ArgumentParser(description='rsidmap')
parser.add_argument('--lift', type=str, default='hg19tohg38')
parser.add_argument('--chr_col', type=str, default='CHR')
parser.add_argument('--pos_col', type=str, default='POS')
parser.add_argument('--file_gwas', type=str, default='./example/df_hg19.txt')
parser.add_argument('--file_out', type=str, default='./example/df_hg19_lifted_to_hg38.txt')
args = parser.parse_args()

lift = args.lift
chr_col = args.chr_col; pos_col = args.pos_col;
file_gwas = args.file_gwas; file_out = args.file_out

print('setting:')
print('lift: '+ lift)
print('chr_col: '+ chr_col); print('pos_col: '+ pos_col)
print('file_gwas: '+ file_gwas); print('file_out: '+ file_out)
print('')

## liftover dict
file_map = {'hg19tohg38': './liftover/hg19ToHg38.over.chain.gz', 'hg38tohg19': './liftover/hg38ToHg19.over.chain.gz'}
## default setting
# lift = 'hg19tohg38'
# chr_col = 'CHR'
# pos_col = 'POS'
# file_gwas = './example/df_hg19.txt'
# file_out = './example/df_hg19_lifted_to_hg38.txt'

# read input
df = pd.read_csv(file_gwas, sep='\t')
df.replace('X', 23, inplace=True) # liftover regonize chr23 but not chrX 
df['id'] = df.index
# make bed
bed = df[[chr_col, pos_col, 'id']].copy()
bed['end'] = bed[pos_col] + 1
bed[chr_col] = 'chr' + bed[chr_col].astype('string')
bed = bed[[chr_col, pos_col, 'end', 'id']]
bed.to_csv(file_gwas+'.bed', sep='\t', index=False, header = False)

# liftover
liftover_command = f'code/liftOver {file_gwas}.bed {file_map[lift]} {file_gwas}.map {file_gwas}.unmap'
subprocess.Popen(liftover_command, shell=True).wait()

# add new pos
df_map = pd.read_csv(f'{file_gwas}.map', sep='\t', header=None)[[1,3]]
df_map.rename(columns = {1:pos_col, 3:'id'}, inplace = True)
df.rename(columns = {pos_col:pos_col+'_old'}, inplace = True)
res = df.merge(df_map, how='left').astype({pos_col: 'Int64'}, errors='ignore').drop('id', axis=1) # ignore NA to int


# save
res.to_csv(file_out, sep='\t', index=False)
print(f'deleting temporary files...')
rm_command = f'rm -rf {file_gwas}.bed {file_gwas}.map {file_gwas}.unmap'
subprocess.Popen(rm_command, shell=True).wait()
print(f'{df_map.shape[0]} snp are lifted successfully')
print(f'done!')
end = time.time()
print (f'spend {round(end-start, 2)} sec')