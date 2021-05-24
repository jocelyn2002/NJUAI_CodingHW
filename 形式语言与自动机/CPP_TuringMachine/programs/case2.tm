#Q = {0,add_m,add_n,left_n,left_check_accept,left_check_reject,right_n,right_check_accept,right_check_reject,accept,accept2,accept3,accept4,halt_accept,reject,reject2,reject3,reject4,reject5,halt_reject}
#S = {1,x,=}
#G = {1,x,=,_,t,r,u,e,f,a,l,s}
#q0 = 0
#B = _
#F = {halt_accept,halt_reject}
#N = 3 ; 1:input 2:store and decrease m  3:store n, decrease n when m reached 0


; State 0: start state
0 1__ 1__ **** add_m   ;input start with 1
0 x__ x__ **** reject  ;input not start with 1, ilegal
0 =__ =__ **** reject  ;as above
0 ___ ___ **** reject  ;as above

; state add_m: scanning the 1st segment of "1^m" x1^n=1^{m+n}
add_m 1__ _1_ rr* add_m  ;still in first part of 1's
add_m x__ ___ r** add_n  ;switch to second part of 1's
add_m =__ =__ r** reject ;ilegal input
add_m ___ ___ *** reject ;as above

; state add_n: scanning the 2nd segment of 1^mx "1^n" =1^{m+n}
add_n 1__ __1 r*r add_n  ;still in second part of 1's
add_n =__ ___ rll left_n ;swich to check final part, tape2 tape3 point to last 1's
add_n x__ x__ r** reject ;ilegal input
add_n ___ ___ *** reject ;as above

; state left_n:
left_n 111 _11 r*l left_n ;tape3 hasn't reach left end, and input remains 1
left_n _11 ___ *** reject ;last part fewer 1
left_n _1_ ___ *l* right_check_accept
left_n 11_ 1__ *l* right_check_reject

right_check_accept ___ ___ *** accept
right_check_accept _1_ ___ *** reject ; last part less 1
right_check_reject 11_ 11_ **r right_n
right_check_reject 1__ 1__ *** reject ; last part more 1

; state right_n
right_n 111 _11 r*r right_n ;tape3 hasn't reach right end, and input remains 1
right_n _11 ___ *** reject ;last part fewer 1
right_n _1_ ___ *l* left_check_accept
right_n 11_ 1__ *l* left_check_reject

left_check_accept ___ ___ *** accept
left_check_accept _1_ ___ *** reject ; last part less 1
left_check_reject 11_ 11_ **l left_n 
left_check_reject 1__ 1__ *** reject ; last part more 1

; reject, clear tape1 and write "false" on tape1
reject 1__ ___ r** reject
reject x__ ___ r** reject
reject =__ ___ r** reject

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
