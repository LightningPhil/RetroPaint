import './style.css';
import { playMarkerPop } from './audio';
import { initCanvas } from './canvas';
import { initInput } from './input';
import { initMaterials } from './materials';
import { startLoop } from './loop';
import { initUi } from './ui';

initCanvas();
initMaterials();
initUi();
initInput();
startLoop();
playMarkerPop();
