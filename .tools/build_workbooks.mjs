import fs from 'node:fs/promises';
import { Workbook, SpreadsheetFile } from '@oai/artifact-tool';

const descriptions = JSON.parse(await fs.readFile('scripts/test_case_descriptions.json','utf8'));
const results = JSON.parse(await fs.readFile('evidence/test-results.json','utf8'));
await fs.mkdir('docs',{recursive:true});

function style(sheet, range, widths) {
  sheet.showGridLines = false;
  const area = sheet.getRange(range);
  area.format.font.name = 'Arial';
  area.format.font.size = 10;
  area.format.verticalAlignment = 'center';
  area.format.wrapText = true;
  for (let index=0; index<widths.length; index++) sheet.getRangeByIndexes(0,index,100,1).format.columnWidth = widths[index];
  sheet.getRange('A2').format.font.size = 16;
  sheet.getRange('A2').format.font.bold = true;
  sheet.getRange('A2:L3').format.wrapText = false;
  sheet.getRange('A2:L3').format.rowHeight = 27;
  sheet.freezePanes.freezeRows(5);
}
function header(sheet,range) {
  sheet.getRange(range).format.fill = '#312E81';
  sheet.getRange(range).format.font.color = '#FFFFFF';
  sheet.getRange(range).format.font.bold = true;
  sheet.getRange(range).format.rowHeight = 30;
}
async function finish(workbook, filename, views) {
  workbook.recalculate();
  console.log((await workbook.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#NUM!',options:{useRegex:true,maxResults:20},summary:'Formula errors'})).ndjson);
  for (const [sheetName,range,suffix] of views) {
    const image = await workbook.render({sheetName,range,scale:1.5,format:'png'});
    await fs.writeFile(`evidence/${suffix}.png`,new Uint8Array(await image.arrayBuffer()));
  }
  const output = await SpreadsheetFile.exportXlsx(workbook);
  await output.save(`docs/${filename}.xlsx`);
}

const tests = Workbook.create();
const sheet = tests.worksheets.add('Test cases');
sheet.getRange('A2').values = [['BlogSphere test cases']];
sheet.getRange('A3').values = [['39 local tests passed; Supabase SSL, migrations and transactional ORM smoke verified. Full PostgreSQL suite pending.']];
const headings = ['Test ID','Feature','Preconditions','Steps','Input','Expected Result','Actual Result','Status','Defect ID','Evidence Link'];
sheet.getRange('A5:J5').values = [headings];
const rows = results.map((record,index)=>{
  const key=record.test.split('.').at(-1).replace(/^test_/,'');
  const [feature,steps,input,expected]=descriptions[key];
  return [`TC-${String(index+1).padStart(2,'0')}`,feature,'Isolated Django test DB; test fixture users/category/posts.',steps,input,expected,record.actual,record.status,'',`../evidence/test-results.json — ${record.test}`];
});
rows.push(['INT-01','Supabase connection','Configured DATABASE_URL','Connect through psycopg; verify SSL; SELECT 1; apply migrations.','Ignored .env connection URI','SSL connection; no pending migrations.','SSL verified; migrations applied; roles initialized.','Pass','','../evidence/supabase-migrations.txt']);
rows.push(['INT-02','PostgreSQL ORM','Migrated Supabase schema','Create related rows; publish/retry/unpublish; protect category; cascade comment; roll back.','Unique temporary test rows','Relationships and workflow correct; no persistent test data.','All smoke assertions passed; transaction rolled back.','Pass','','../evidence/postgresql-smoke.txt']);
rows.push(['INT-03','Full PostgreSQL suite','Dedicated isolated PostgreSQL test database','Run complete Django/browser suite against dedicated PostgreSQL test database.','Separate authorized test database','Full suite passes on PostgreSQL.','Not executed against a dedicated PostgreSQL test database.','Not Run','','../docs/final-report.md']);
sheet.getRange(`A6:J${rows.length+5}`).values=rows;
style(sheet,`A1:J${rows.length+5}`,[13,25,35,55,38,50,34,13,13,60]);
sheet.getRange(`A6:J${rows.length+5}`).format.rowHeight=76;
header(sheet,'A5:J5');
sheet.getRange(`H6:H${rows.length+5}`).dataValidation={rule:{type:'list',values:['Pass','Fail','Not Run','Blocked']}};
sheet.getRange(`H6:H${rows.length+5}`).conditionalFormats.add('containsText',{text:'Blocked',format:{fill:'#FEF3C7'}});
sheet.tables.add(`A5:J${rows.length+5}`,true,'TestCases');
console.log((await tests.inspect({kind:'table',range:'Test cases!F5:J9',include:'values',tableMaxRows:5,tableMaxCols:5})).ndjson);
await finish(tests,'test-cases',[['Test cases','A1:E9','test-cases-preview'],['Test cases','F5:J9','test-results-preview']]);

const costs=Workbook.create();
const budget=costs.worksheets.add('Monthly budget');
const workload=costs.worksheets.add('Workload');
budget.getRange('A2').values=[['BlogSphere deployment budgets (USD/month)']];
budget.getRange('A3').values=[['Illustrative estimates only. Replace amber inputs with verified regional quotes; no vendor quotation is implied.']];
budget.getRange('A5:L5').values=[['Approach','Users','Compute','Database','Storage','Backups','Bandwidth','Monitoring','Domain','Maintenance hours','Labor cost','Total incl. labor']];
const plans=[
 ['VPS',100,12,25,0,5,0,2,1.25,2],['VPS',1000,24,25,2,10,0,5,1.25,3],
 ['VPS',10000,80,75,5,25,10,18,1.25,5.5],['VPS',1000000,800,750,50,150,750,125,1.25,32],
 ['AWS',100,12,25,0,5,0,2,1.25,3],['AWS',1000,32,25,5,12,12,10,1.25,4],
 ['AWS',10000,160,75,12,35,40,61,1.25,8],['AWS',1000000,1600,1000,100,250,1800,195,1.25,48]
];
budget.getRange('A6:J13').values=plans;
for(let row=6;row<=13;row++) {
 budget.getRange(`K${row}`).formulas=[[`=J${row}*Workload!B14`]];
 budget.getRange(`L${row}`).formulas=[[`=SUM(C${row}:I${row},K${row})`]];
}
budget.getRange('A16:B20').values=[['Sources (verify quotes)','Reference'],['VPS pricing','https://www.digitalocean.com/pricing/droplets'],['AWS pricing','https://aws.amazon.com/lightsail/pricing/'],['Supabase pricing','https://supabase.com/pricing'],['AWS calculator','https://calculator.aws/']];
style(budget,'A1:L20',[24,15,15,15,15,15,16,16,15,21,17,20]);
header(budget,'A5:L5');
budget.getRange('C6:J13').format.fill='#FEF3C7';
budget.getRange('C6:I13').setNumberFormat('"$"#,##0.00');
budget.getRange('K6:L13').setNumberFormat('"$"#,##0.00');
budget.getRange('B6:B13').setNumberFormat('#,##0');
budget.getRange('A6:L13').format.rowHeight=30;
budget.getRange('A16:B20').format.rowHeight=40;
budget.getRange('A16:B20').format.wrapText=false;

workload.getRange('A2').values=[['Workload assumptions and capacity']];
workload.getRange('A3').values=[['Planning assumptions, not measured traffic. Decimal KB/GB; 30-day month.']];
workload.getRange('A5:B14').values=[['Driver','Value'],['Daily active share',0.2],['Requests / active user / day',20],['Response KB',100],['Days / month',30],['Peak multiplier',10],['Monthly articles / registered user',0.02],['KB per article incl. comments',50],['DB overhead multiplier',3],['Labor USD/hour (hypothetical)',40]];
workload.getRange('A17:E17').values=[['Users','Monthly requests','Transfer GB/month','Peak requests/sec','DB growth GB/month']];
for (const [offset,users] of [100,1000,10000,1000000].entries()) {
 const row=18+offset;
 workload.getRange(`A${row}`).values=[[users]];
 workload.getRange(`B${row}:E${row}`).formulas=[[`=A${row}*$B$6*$B$7*$B$9`,`=B${row}*$B$8/1000000`,`=B${row}/($B$9*86400)*$B$10`,`=A${row}*$B$11*$B$12*$B$13/1000000`]];
}
workload.getRange('A24:B28').values=[['Users','Capacity approach (requires load testing)'],[100,'One small app instance; Supabase PostgreSQL; daily backups.'],[1000,'Monitor memory/queries; modest instance upgrade if measured demand requires.'],[10000,'Larger or two app nodes; connection budget; database/search tuning.'],[1000000,'Multiple app nodes + load balancer; static CDN; larger DB/replicas; tested failover.']];
style(workload,'A1:E28',[38,42,25,25,28]);
header(workload,'A5:B5'); header(workload,'A17:E17'); header(workload,'A24:B24');
workload.getRange('B6:B14').format.fill='#FEF3C7';
workload.getRange('B6').setNumberFormat('0%');
workload.getRange('A18:B21').setNumberFormat('#,##0');
workload.getRange('C18:E21').setNumberFormat('0.0000');
workload.getRange('A25:B28').format.rowHeight=70;
costs.recalculate();
const originalLabor=workload.getRange('B14').values[0][0];
workload.getRange('B14').values=[[50]];
costs.recalculate();
if (budget.getRange('K6').values[0][0] !== 100) throw new Error('Labor sensitivity failed');
workload.getRange('B14').values=[[originalLabor]];
workload.getRange('B6').values=[[0.1]];
costs.recalculate();
if (workload.getRange('B18').values[0][0] !== 6000) throw new Error('Traffic sensitivity failed');
workload.getRange('B6').values=[[0.2]];
costs.recalculate();
console.log((await costs.inspect({kind:'table',range:'Monthly budget!K5:L13',include:'values,formulas',tableMaxRows:9,tableMaxCols:2})).ndjson);
console.log((await costs.inspect({kind:'table',range:'Workload!A17:E21',include:'values,formulas',tableMaxRows:5,tableMaxCols:5})).ndjson);
await finish(costs,'cost-and-scaling',[['Monthly budget','A1:F13','cost-budget-preview'],['Monthly budget','G5:L13','cost-totals-preview'],['Workload','A1:E28','cost-workload-preview']]);
