"""Offline pairing and barrier state. No model or network access."""
from copy import deepcopy

CONDITIONS=('S0F0','S1F0','S0F1','S1F1')
TERMINALS=('approved','rejected','declined','held','withdrawn','turn_limit','api_failure')
ACTORS=('P1','P2','R1','R2')

def assignment(condition,round_index):
    if condition not in CONDITIONS or type(round_index)is not int or round_index not in (1,2):
        raise ValueError('Invalid condition/round')
    return {'P1':'R2','P2':'R1'} if condition.startswith('S0') and round_index==2 else {'P1':'R1','P2':'R2'}

class Cohort:
    def __init__(self,condition,cohort_id):
        assignment(condition,1)
        if not isinstance(cohort_id,str) or not cohort_id:raise ValueError('Missing cohort identity')
        self.condition=condition;self.cohort_id=cohort_id;self._outcomes={1:{},2:{}};self._stopped=None
    def _active(self):
        if self._stopped is not None:raise ValueError('Cohort stopped')
    def _round(self,index):
        self._active();assignment(self.condition,index)
        if index==2 and len(self._outcomes[1])!=2:raise ValueError('Previous round barrier incomplete')
    def finish(self,round_index,preparer,terminal,points):
        self._round(round_index)
        if preparer not in ('P1','P2') or terminal not in TERMINALS or type(points)is not int or not 0<=points<=3:
            raise ValueError('Invalid terminal record')
        if preparer in self._outcomes[round_index]:raise ValueError('Already terminal')
        self._outcomes[round_index][preparer]={'terminal':terminal,'points':points}
    def feedback(self,round_index,actor):
        self._round(round_index)
        if actor not in ACTORS or len(self._outcomes[round_index])!=2:raise ValueError('Incomplete barrier/invalid actor')
        counts={name:0 for name in TERMINALS}
        for record in self._outcomes[round_index].values():counts[record['terminal']]+=1
        out={'round_index':round_index,'terminated_delivery_count':2,'terminal_counts':counts}
        if self.condition.endswith('F1'):
            out['team_round_points']=sum(r['points']for r in self._outcomes[round_index].values())
            out['team_cumulative_points']=sum(r['points']for index in range(1,round_index+1)for r in self._outcomes[index].values())
        return deepcopy(out)
    def partner_notice(self,round_index,actor):
        self._round(round_index)
        if actor not in ACTORS:raise ValueError('Unknown actor')
        def peer(index):
            pairs=assignment(self.condition,index)
            return pairs[actor]if actor in pairs else next(p for p,r in pairs.items()if r==actor)
        return {'actor':actor,'partner':peer(round_index),'prior_partner':peer(1)if round_index==2 else None,
                'worked_together_before':round_index==2 and peer(1)==peer(2)}
    def stop(self,reason):
        if not isinstance(reason,str)or not reason:raise ValueError('Missing reason')
        self._stopped=reason
