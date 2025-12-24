from types import SimpleNamespace
from enum import Enum

MAX_SIGNAL_LEN = 5000
FREQUENCY = 500  # измерений в секунду

TYPES_OF_STEP = SimpleNamespace(
    candidates='candidates',
    signal='signal'
)


JSON_KEYS = SimpleNamespace(
    STEP_ID_IN_TRACK = 'step_id',
    STEP_CLASS_NAME = 'step_class',
    STEP_ARGS = 'step_args',
    TRACK_ID_IN_MULTITRACK = "track_id"
)


PADDING = 0.3  #  о размере фрагмента сигнала в окне этого просмотрщика

LEADS_NAMES = SimpleNamespace(
    i='i',
    ii='ii',
    iii='iii',
    avr='avr',
    avl='avl',
    avf='avf',
    v1='v1',
    v2='v2',
    v3='v3',
    v4='v4',
    v5='v5',
    v6='v6',
)

LEADS_NAMES_ORDERED = [LEADS_NAMES.i, LEADS_NAMES.ii, LEADS_NAMES.iii,
                       LEADS_NAMES.avr, LEADS_NAMES.avl, LEADS_NAMES.avf,
                       LEADS_NAMES.v1, LEADS_NAMES.v2, LEADS_NAMES.v3, LEADS_NAMES.v4, LEADS_NAMES.v5, LEADS_NAMES.v6]

# Переменные, связанные с точками разметки

WAVES_TYPES = SimpleNamespace(
    P='p',
    QRS='qrs',
    T='t',
    NO_WAVE='nowave'
)

class POINTS_TYPES(Enum):
    T_START = 1
    T_PEAK = 2
    T_END = 3

    P_START = 4
    P_PEAK = 5
    P_END = 6

    QRS_START = 7
    QRS_PEAK = 8
    QRS_END = 9

#  Общие настройки рисования:

# вертикальные линии разметки
DELINEATION_LINEWIDTH = 1.1

# рисование сигнала на миллиметровке:
SIGNAL_LINEWIDTH = 1
MINOR_GRID_LINEWIDTH = 0.2
MAJOR_GRID_LINEWITH = 0.6
SIGNAL_COLOR =  (0.1,0.3,0.5)
GRID_COLOR = 'gray'

POINTS_TYPES_COLORS = {
    POINTS_TYPES.T_START: '#712342',
    POINTS_TYPES.T_PEAK: '#371261',
    POINTS_TYPES.T_END: '#601962',

    POINTS_TYPES.QRS_PEAK : '#239731',
    POINTS_TYPES.QRS_END : '#562147',
    POINTS_TYPES.QRS_START : '#622508',

    POINTS_TYPES.P_END : '#712342',
    POINTS_TYPES.P_START : '#711142',
    POINTS_TYPES.P_PEAK : '#714442'
    }