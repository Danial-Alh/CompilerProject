program firstProgram
int a := #2;
procedure func ()
{
	boolean test:=true;
	char x[#12], y[#3];
	{
	    //x[#6] := +(x[y[#3]],\o);
	    //x[#5] := +(and then(false, or else(true, test)), #2);
		//x:= #2;
		//if and then(#3, true) then
        //else a := #5;
        //for a := #2 upto #5 do test := false;
        //do {test := false; a := +(a, #10);} while <(a , #5);
        switch a case #700: {a := #701;} case #800: {a := #801;} default: {a := #901;} end;
	}
};
main
{
    a:=#2;
}