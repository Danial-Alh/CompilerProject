program firstProgram 
int a, b:=#2, c:=#15, d[#1 .. #3]:={#4,#3,#2}, e[b*#2+#1 .. b*#3+c], f[#10];
int x:=#10;
real g:=#1.003, h, i:=#20.03;
char j:='c', k:=\e;
boolean w:=true;
boolean b := true;
int array[#2] := {#1, #7};
char chars[i..k] := {'c', 'd', '7'};
procedure func 0(int n;) 
{
	int x:=#1;
	int y:=#2;
	boolean test:=True;
	{
		if < (x,y)
		then 
		x:= +(x, #1)
		else
		y:= -(y, #1);
		
		do 
		x:=+(x,#1)
		while <(x, #1);
		
		*(d[#1],#2);
		
		//comment
		
		for i:=#1 upto #10
		do +(j,+(i,#2));
		
		return j;
	}
};
procedure func (int input; boolean which;) {
        int mid := #2;
         int c := +(input, \3);
         {
            if and then(which, true) then return +(c, mid);
            else return -(c, mid);
         }
    };

    procedure abs (int input;)
    {
        {
            if >(input, \0) then return input;
            else return *(-#1, input);
        }
    };
main 
{
	a:=#2;
	switch +(a,#2)
	case #4: 
	{
		a:=+(a, #1);
	}
	case #5:
	{
		a:=-(a, #1);
	}
	default:
	{
		a:=*(a, #1);
	}
	end
	d[#1]:=#2;
	
}