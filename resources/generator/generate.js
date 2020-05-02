var fs = require('fs');

const { registerFont } = require('canvas')
registerFont(
    __dirname + "/AkzidenzGrotesk/AkzidenzGrotesk-Cond.otf",
    {
        family : "AkzidenzGrotesk-Cond"
    }
)

var svg2img = require('svg2img');
const template = fs.readFileSync( __dirname+'/template.svg', 'utf-8' );

let glyphs = [];
// generate number characters from ascii char codes
for (let c = 48; c < 58; c++) { glyphs.push( String.fromCharCode(c) ) };
// generate uppercase A-Z from ascii char chodes
for (let c = 65; c < 91; c++) { glyphs.push( String.fromCharCode(c) ) };

for (const glyph of glyphs) {
    
    const generated = template.replace( "$glyph", glyph );
    
    svg2img( generated, function(error, buffer) {
        fs.writeFileSync( 'images/' + glyph + '.png', buffer );
    });    
}

 