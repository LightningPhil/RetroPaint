import './style.css';
import { playMarkerPop } from './audio';
import { initCanvas } from './canvas';
import { initInput } from './input';
import { initMaterials } from './materials';
import { startLoop } from './loop';
import { loadLevel } from './state';
import { initUi } from './ui';

loadLevel();
initCanvas();
initMaterials();
initUi();
initInput();
startLoop();
playMarkerPop();
