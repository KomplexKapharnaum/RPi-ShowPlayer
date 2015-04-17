#ifndef ____myfont__
#define ____myfont__


// copied from http://heim.ifi.uio.no/haakoh/avr/a
const int font_count = 159;
const unsigned char myfont[159][6] = {
  {0, 0, 0, 0, 0, 0}, // space! 32
  {0x0, 0x0, 0x79, 0x0, 0x0, 0x0},  // !
{0x0, 0x70, 0x0, 0x70, 0x0, 0x0},  // "
{0x14, 0x7f, 0x14, 0x7f, 0x14, 0x0},  // #
{0x12, 0x2a, 0x7f, 0x2a, 0x24, 0x0}, // $
{0x62, 0x64, 0x8, 0x13, 0x23, 0x0},  // %
{0x36, 0x49, 0x55, 0x22, 0x5, 0x0},  // &
{0x0, 0x50, 0x60, 0x0, 0x0, 0x0},  // '
{0x0, 0x1c, 0x22, 0x41, 0x0, 0x0},// (
{0x0, 0x41, 0x22, 0x1c, 0x0, 0x0}, // )
{0x14, 0x8, 0x3e, 0x8, 0x14, 0x0}, // *      /42
{0x8, 0x8, 0x3e, 0x8, 0x8, 0x0},  // +
{0x0, 0x5, 0x6, 0x0, 0x0, 0x0}, // ,
{0x8, 0x8, 0x8, 0x8, 0x8, 0x0},  // -
{0x0, 0x3, 0x3, 0x0, 0x0, 0x0},  // .
{0x2, 0x4, 0x8, 0x10, 0x20, 0x0},  // /
  {0x3e, 0x45, 0x49, 0x51, 0x3e, 0},  //
  {0x00, 0x10, 0x20, 0x7f, 0x00, 0},
  {0x47, 0x49, 0x49, 0x49, 0x31, 0},
  {0x42, 0x49, 0x59, 0x69, 0x46, 0},
  {0x08, 0x18, 0x28, 0x7f, 0x08, 0},          //52
  {0x71, 0x49, 0x49, 0x49, 0x46, 0},
  {0x3e, 0x49, 0x49, 0x49, 0x06, 0},
  {0x40, 0x47, 0x48, 0x50, 0x60, 0},
  {0x36, 0x49, 0x49, 0x49, 0x36, 0},
  {0x30, 0x49, 0x49, 0x49, 0x3e, 0}, //
  {0x0, 0x36, 0x36, 0x0, 0x0, 0x0}, // :
  {0x0, 0x35, 0x36, 0x0, 0x0, 0x0}, // ;
  {0x8, 0x14, 0x22, 0x41, 0x0, 0x0},// <
  {0x14, 0x14, 0x14, 0x14, 0x14, 0x0}, // =
  {0x0, 0x41, 0x22, 0x14, 0x8, 0x0}, // >       /62
  {0x20, 0x40, 0x45, 0x48, 0x30, 0x0}, // ?
  {0x26, 0x49, 0x4f, 0x41, 0x3e, 0x0}, // @
  {0x3f, 0x48, 0x48, 0x48, 0x3f, 0}, // A
  {0x7f, 0x49, 0x49, 0x49, 0x36, 0}, // B
  {0x3e, 0x41, 0x41, 0x41, 0x22, 0}, // C
  {0x7f, 0x41, 0x41, 0x22, 0x1c, 0}, // D
  {0x7f, 0x49, 0x49, 0x49, 0x41, 0}, // E
  {0x7f, 0x48, 0x48, 0x48, 0x40, 0}, // F
  {0x3e, 0x41, 0x49, 0x49, 0x2e, 0}, // G
  {0x7f, 0x08, 0x08, 0x08, 0x7f, 0}, // H       /72
  {0x00, 0x41, 0x7f, 0x41, 0x00, 0}, // I
  {0x06, 0x01, 0x01, 0x01, 0x7e, 0}, // J
  {0x7f, 0x08, 0x14, 0x22, 0x41, 0}, // K
  {0x7f, 0x01, 0x01, 0x01, 0x01, 0}, // L
  {0x7f, 0x20, 0x10, 0x20, 0x7f, 0}, // M
  {0x7f, 0x10, 0x08, 0x04, 0x7f, 0}, // N
  {0x3e, 0x41, 0x41, 0x41, 0x3e, 0}, // O
  {0x7f, 0x48, 0x48, 0x48, 0x30, 0},  // P
  {0x3e, 0x41, 0x45, 0x42, 0x3d, 0},
  {0x7f, 0x48, 0x4c, 0x4a, 0x31, 0},            //82
  {0x31, 0x49, 0x49, 0x49, 0x46, 0},
  {0x40, 0x40, 0x7f, 0x40, 0x40, 0},
  {0x7e, 0x01, 0x01, 0x01, 0x7e, 0},
  {0x7c, 0x02, 0x01, 0x02, 0x7c, 0},
  {0x7f, 0x02, 0x04, 0x02, 0x7f, 0},
  {0x63, 0x14, 0x08, 0x14, 0x63, 0},
  {0x60, 0x10, 0x0f, 0x10, 0x60, 0},
  {0x43, 0x45, 0x49, 0x51, 0x61, 0},  //
   {0x0, 0x7f, 0x41, 0x41, 0x0, 0x0},  // [
   {0x20, 0x10, 0x8, 0x4, 0x2, 0x0},  // backslash        /92
   {0x0, 0x41, 0x41, 0x7f, 0x0, 0x0},  // ]
   {0x0, 0x20, 0x40, 0x40, 0x20, 0x0},  // ^
   {0x1, 0x1, 0x1, 0x1, 0x1, 0x0},   // _
  {0x3, 0x7, 0x7e, 0x20, 0x1c, 0x0},   // grave accent -> note de musique
  {0x02, 0x15, 0x15, 0x15, 0x0F, 0}, // a 97
  {0x7f, 0x5, 0x9, 0x9, 0x6, 0x0}, // b
  {0xe, 0x11, 0x11, 0x11, 0x2, 0x0}, // c
  {0x6, 0x9, 0x9, 0x5, 0x7f, 0x0}, // d
  {0xe, 0x15, 0x15, 0x15, 0xc, 0x0}, // e
  {0x8, 0x3f, 0x48, 0x40, 0x20, 0x0}, // f                /102
  {0x18, 0x25, 0x25, 0x25, 0x3e, 0x0}, // g
  {0x7f, 0x8, 0x10, 0x10, 0xf, 0x0}, // h
  {0x0, 0x0, 0x2f, 0x0, 0x0, 0x0}, // i
  {0x2, 0x1, 0x11, 0x5e, 0x0, 0x0}, // j
  {0x7f, 0x4, 0xa, 0x11, 0x0, 0x0}, // k
  {0x0, 0x41, 0x7f, 0x1, 0x0, 0x0}, // l
  {0x1f, 0x10, 0xc, 0x10, 0xf, 0x0}, // m
  {0x1f, 0x8, 0x10, 0x10, 0xf, 0x0}, // n
  {0xe, 0x11, 0x11, 0x11, 0xe, 0x0}, // o
  {0x1f, 0x14, 0x14, 0x14, 0x8, 0x0},  // p             //112
  {0x8, 0x14, 0x14, 0xc, 0x1f, 0x0},
  {0x1f, 0x8, 0x10, 0x10, 0x8, 0x0},
  {0x9, 0x15, 0x15, 0x15, 0x2, 0x0},
  {0x10, 0x3e, 0x11, 0x1, 0x2, 0x0},
  {0x1e, 0x1, 0x1, 0x2, 0x1f, 0x0},
  {0x1c, 0x2, 0x1, 0x2, 0x1c, 0x0},
  {0x1e, 0x1, 0x6, 0x1, 0x1e, 0x0},
  {0x11, 0xa, 0x4, 0xa, 0x11, 0x0},
  {0x18, 0x5, 0x5, 0x5, 0x1e, 0x0},
  {0x11, 0x13, 0x15, 0x19, 0x11, 0x0},// z 122             /122
  {0x8, 0x1c, 0x3e, 0x1c, 0x1c, 0x1c},   // { remplacé par flèche à gauche
  {0x5e, 0x52, 0x5a, 0x42, 0x7e, 0x0},   // | remplacé par spirale
  {0x1c, 0x1c, 0x1c, 0x3e, 0x1c, 0x8},   // } remplacé par flèche à droite
  {0x1c, 0x3e, 0x7f, 0x57, 0x22, 0x0},   //~ remplacé par pacman ouvert
  {0x1c, 0x3e, 0x7f, 0x5f, 0x3e, 0x1c},   //del remplacé par pacman fermé
  
  {0x1f, 0x28, 0xa8, 0x68, 0x1f, 0x0},    // 192 À
  {0x1f, 0x68, 0xa8, 0x28, 0x1f, 0x0},    //193 Á
  {0x1f, 0x68, 0xa8, 0x68, 0x1f, 0x0},   //194 Â
  {0x1f, 0x68, 0xa8, 0x68, 0x9f, 0x0},   //195 Ã
  {0x1f, 0xa8, 0x28, 0xa8, 0x1f, 0x0},   //196 Ä          /132
  {0x1c, 0x3e, 0x7f, 0x57, 0x22, 0x0},   //197 pacman ouvert
  {0x1c, 0x3e, 0x7f, 0x5f, 0x3e, 0x1c},   //198 pacman fermé
  {0x1c, 0x22, 0x23, 0x22, 0x4, 0x0},   //199 Ç remplacé par ç minuscule
  {0x3f, 0xa9, 0x69, 0x29, 0x21, 0x0},   //200 È
  {0x3f, 0x69, 0xa9, 0x29, 0x21, 0x0},   //201 É
  {0x3f, 0x69, 0xa9, 0x69, 0x21, 0x0},   //202 Ê
  {0x3f, 0xa9, 0x29, 0xa9, 0x21, 0x0},   //203 Ë
  {0x5e, 0x52, 0x5a, 0x42, 0x7e, 0x0},   //204 Ì remplacé par spirale
  {0x18, 0x3c, 0x1e, 0x3c, 0x18, 0x0},   //205 Í remplacé par cœur
  {0x0, 0x51, 0x9f, 0x51, 0x0, 0x0},   //206 Î          /142
  {0x0, 0xa1, 0x3f, 0xa1, 0x0, 0x0},   //207 Ï
  {0xff, 0xff, 0xff, 0xff, 0xff, 0},   //208 Đ remplacé par bloc plein isolé
  {0xff, 0xff, 0xff, 0xff, 0xff, 0xff},   //209 Ñ remplacé par bloc plein collé
  {0x55, 0xaa, 0x55, 0xaa, 0x55, 0x0},   //210 Ò remplacé par damier isolé
  {0x55, 0xaa, 0x55, 0xaa, 0x55, 0xaa},   //211 Ó remplacé par damier collé
  {0x1e, 0x61, 0xa1, 0x61, 0x1e, 0x0},   //212 Ô
  {0x1c, 0x1c, 0x1c, 0x3e, 0x1c, 0x8},   //213 Õ remplacé par flèche à droite
  {0x8, 0x1c, 0x3e, 0x1c, 0x1c, 0x1c},   //214 Ö remplacé par flèche à gauche
  {0x20, 0x7e, 0xfe, 0x7e, 0x20, 0x0},   //215 × remplacé par flèche vers le haut
  {0x4, 0x7e, 0x7f, 0x7e, 0x4, 0x0},   //216 Ø remplacé par flèche vers le bas    /152
  {0x3e, 0x1, 0x41, 0x81, 0x3e, 0x0},   //217 Ú
  {0x3e, 0x81, 0x41, 0x1, 0x3e, 0x0},   //218 Ù
  {0x1e, 0x41, 0x81, 0x41, 0x1e, 0x0},   //219 Û
  {0x3e, 0x81, 0x1, 0x81, 0x3e, 0x0},   //220 Ü
  {0x70, 0xdb, 0xfa, 0xdb, 0x70, 0x0},   //221 Ý remplacé par tête de mort   //
  {0x62, 0x61, 0xd, 0x61, 0x62, 0x0},   //222 Þ remplacé par smiley
  {0xbb, 0xaa, 0xaa, 0xaa, 0xaa, 0xee},   //223 ß remplacé par serpent
  {0x2, 0x15, 0x55, 0x35, 0xf, 0x0},   //224 à
  {0x2, 0x15, 0x35, 0x55, 0xf, 0x0},   //225 á
  {0x2, 0x55, 0x95, 0x55, 0xf, 0x0},   //226 â        /162
  {0x2, 0x55, 0x95, 0x55, 0x8f, 0x0},   //227 ã
  {0x2, 0x55, 0x15, 0x55, 0xf, 0x0},   //228 ä          /
  {0x4, 0x8, 0x4, 0x28, 0x30, 0x38},   //229 å remplacé par flèche de la bourse qui monte
  {0x55, 0x55, 0x55, 0x55, 0x55, 0x0},   //230 æ remplécé par rayure horizontale collée
  {0x1c, 0x22, 0x23, 0x22, 0x4, 0x0},   //231 ç           //
  {0xe, 0x15, 0x55, 0x35, 0xc, 0x0},   //232 è
  {0xe, 0x15, 0x55, 0x95, 0xc, 0x0}, // 233 é
  {0xe, 0x55, 0x95, 0x55, 0xc, 0x0},   //234 ê
  {0xe, 0x55, 0x15, 0x55, 0xc, 0x0},   //235 ë
  {0x49, 0x92, 0x49, 0x24, 0x49, 0},   //236 ì remplacé par vague isolée    /172
  {0x49, 0x92, 0x49, 0x24, 0x49, 0x92},   //237 í replacé par vague collée
  {0x0, 0x20, 0x4f, 0x20, 0x0, 0x0},   //238 î
  {0x0, 0x20, 0xf, 0x20, 0x0, 0x0},   //239 ï
  {0xe7, 0x81, 0x0, 0x81, 0xe7, 0x0},   //240 đ remplacé par cadre
  {0x1f, 0x48, 0x90, 0x50, 0x8f, 0x0},   //241 ñ            /
  {0xc, 0x92, 0x96, 0x92, 0x4c, 0x0},   //242 ò remplacé par œil gauche
  {0xc, 0x52, 0x96, 0x92, 0x8c, 0x0},   //243 ó remplacé par œil droit
  {0xe, 0x51, 0x91, 0x51, 0xe, 0x0},   //244 ô
  {0x8, 0x44, 0x84, 0x84, 0x98, 0x8},   //245 õ remplacé par clin d'œil droit
  {0xe, 0x51, 0x11, 0x51, 0xe, 0x0},   //246 ö              /182
  {0x0, 0xaa, 0x0, 0x55, 0x0, 0xa5},   //247 ÷ remplacé par motif léger collé
  {0x1c, 0x49, 0x63, 0x49, 0x1c, 0x0},   //248 ø remplacé par cible
  {0x1e, 0x41, 0x21, 0x2, 0x1f, 0x0},   //249 ù
  {0x1e, 0x1, 0x21, 0x42, 0x1f, 0x0},   //250 ú
  {0x1e, 0x41, 0x81, 0x42, 0x1f, 0x0},   //251 û        //
  {0x1e, 0x41, 0x1, 0x42, 0x1f, 0x0},   //252 ü
  {0xe, 0x11, 0xe, 0x15, 0xd, 0x0}, //253 œ au lieu de 156
  {0x3e, 0x41, 0x3e, 0x49, 0x41, 0x0}, //254 Œ au lieu de 140 //190 ->tableau de
 
};


#endif /* defined(____myfont__) */