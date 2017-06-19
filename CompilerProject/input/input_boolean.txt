program firstProgram
int a := #2;
char c := \i;
procedure func ()
{
	boolean test:=true;
	char x[#1..#12];
	char y[#3];
	{
	    //c := +(c, #2);

        y[#2] := \o;
	    x[#6] := \o;
	    x := +(x[y[#2]],#4);
	    //x[#5] := +(and then(false, or else(true, test)), #2);
		//x[#6] := #2;
		//if and then(#6, true) then a:=#4
        //else a := #5;
        //for a := #2 upto #5 do {print a;};
        //do {a := +(a, #1); print a;} while <(a , #5);
        //switch or else(false, false) case #1: {a := #701;} case #0: {a := #901;} end;
        //print a;
        print x[#6];
	}
};
main
{
    a:=#2;
}