// node scripts/export_book.js poems.json options.json  -> prints {path: xml} JSON for the .docx parts
// poems.json: [{title, text, mode, meter}] (as stored in the Diwan); options: {bookTitle, font, tashkeel, appendix, meterUnderTitle}
const fs = require('fs'), path = require('path');
const A = require('../assets/workbench/engine.js');
A.load(JSON.parse(fs.readFileSync(path.join(__dirname, '../assets/workbench/meters.json'), 'utf8')));
const E = require('../assets/workbench/export.js');
const poems = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const opts = process.argv[3] ? JSON.parse(fs.readFileSync(process.argv[3], 'utf8')) : {};
const model = Object.assign({ tashkeel: 'full', appendix: false, font: 'Traditional Arabic' }, opts, { poems: poems.map(p => E.poemModel(p, A)) });
if (opts.textOnly) process.stdout.write(JSON.stringify({ text: E.plainText(model) }));
else process.stdout.write(JSON.stringify(E.build(model)));
