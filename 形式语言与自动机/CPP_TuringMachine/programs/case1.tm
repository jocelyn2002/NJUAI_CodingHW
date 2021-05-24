#Q = {0,push_a,push_b,pop_a,pop_b,accept,accept2,accept3,accept4,halt_accept,reject,reject2,reject3,reject4,reject5,halt_reject}
#S = {a,b}
#G = {a,b,_,t,r,u,e,f,a,l,s}
#q0 = 0
#B = _
#F = {halt_accept,halt_reject}
#N = 3


; State 0: start state
0 a__ a__ *** push_a   ;input start with a
0 b__ b__ *** reject  ;input not start with a, reject
0 ___ ___ *** reject  ;empty input, reject

; state push_a: scanning the 1st segment of "a^i" b^ja^ib^j
push_a a__ _a_ rr* push_a
push_a b__ b__ *** push_b
push_a ___ ___ *** reject

; state push_b: scanning the 2nd segment of a^i "b^j" a^ib^j
push_b b__ __b r*r push_b
push_b a__ a__ *l* pop_a
push_b ___ ___ *** reject ; no a to pop

; state pop_a: scanning the 3rd segment of a^ib^j "a^i" b^j
pop_a aa_ ___ rl* pop_a
pop_a a__ a__ *** reject ; over pop
pop_a ba_ b__ *** reject ; over push
pop_a b__ b__ **l pop_b
pop_a ___ ___ *** reject ; no b to pop
pop_a _a_ ___ *** reject ; no b to pop

; state pop_b: scanning the 4th segment of a^ib^ja^i "b^j"
pop_b b_b ___ r*l pop_b 
pop_b b__ b__ *** reject ; over pop
pop_b __b ___ *** reject ; over push
pop_b ___ ___ *** accept

; reject, clear tape1 and write "false" on tape1
reject a__ ___ r** reject
reject b__ ___ r** reject

reject ___ f__ r** reject2
reject2 ___ a__ r** reject3
reject3 ___ l__ r** reject4
reject4 ___ s__ r** reject5
reject5 ___ e__ *** halt_reject

; accept, all tapes must be already cleared, just write "true" on tape1
accept ___ t__ r** accept2
accept2 ___ r__ r** accept3
accept3 ___ u__ r** accept4
accept4 ___ e__ *** halt_accept
