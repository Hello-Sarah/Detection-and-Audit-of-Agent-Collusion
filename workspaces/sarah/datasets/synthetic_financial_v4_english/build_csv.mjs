// Build machine-readable CSV exports from actual SQLite queries via Artifact Tool.
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
import {Workbook} from '@oai/artifact-tool';

const source=path.dirname(fileURLToPath(import.meta.url));
const output=path.resolve(process.argv[2]||source);
const python=process.env.DATASET_PYTHON||'python3';
const scratch=await fs.mkdtemp(path.join(os.tmpdir(),'sarah-synthetic-data-'));
const payload=path.join(scratch,'tables.json');
const result=spawnSync(python,[path.join(source,'generate_dataset.py'),output,payload],{encoding:'utf8'});
if(result.status!==0)throw new Error(result.stderr||result.stdout);
process.stdout.write(result.stdout);
const tables=JSON.parse(await fs.readFile(payload,'utf8'));
const wb=Workbook.create();
const matrices={};
for(const [name,rows] of Object.entries(tables)){
  const columns=Object.keys(rows[0]);
  const matrix=[columns,...rows.map(r=>columns.map(c=>r[c]))];
  matrices[name]=matrix;
  const sheet=wb.worksheets.add(name);
  sheet.getRangeByIndexes(0,0,matrix.length,columns.length).values=matrix;
  sheet.getRangeByIndexes(0,0,matrix.length,columns.length).format.columnWidth=28;
  sheet.freezePanes.freezeRows(1);
}
wb.recalculate();
await fs.mkdir(path.join(output,'csv'),{recursive:true});
const encode=value=>{
 const text=String(value??'');
 return /[",\r\n]/.test(text)?'"'+text.replaceAll('"','""')+'"':text;
};
for(const [name,matrix] of Object.entries(matrices)){
 const actual=wb.worksheets.getItem(name).getRangeByIndexes(0,0,matrix.length,matrix[0].length).values;
 if(JSON.stringify(actual)!==JSON.stringify(matrix))throw new Error('Cell roundtrip mismatch: '+name);
 const csv=actual.map(row=>row.map(encode).join(',')).join('\n')+'\n';
 await fs.writeFile(path.join(output,'csv',name+'.csv'),csv,{flag:'wx'});
}
const inspect=await wb.inspect({kind:'table',range:'aggregates!A1:B3',include:'values',tableMaxRows:3,tableMaxCols:2,maxChars:1000});
console.log(inspect.ndjson);
const check=spawnSync(python,[path.join(source,'verify_dataset.py'),output],{encoding:'utf8'});
if(check.status!==0)throw new Error(check.stderr||check.stdout);
process.stdout.write(check.stdout);
await fs.rm(scratch,{recursive:true});
console.log('Created seven flat UTF-8 CSV files and verified SQLite/fixture consistency.');
