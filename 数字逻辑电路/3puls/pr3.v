module pr3(in_x,out_c,SEGS,neg);
	input [8:0] in_x;
	output reg [2:0] out_c;
	output reg neg;
	output reg [6:0] SEGS;
	reg [3:0] c,s,a,b;

	always @(in_x)
	begin
		a = in_x[4:1];
		b = in_x[8:5];
		if (a[3]==1) 
		begin
		a[3]=0;
		a=~a+1;
		end
		if (b[3]==1) 
		begin
		b[3]=0;
		b=~b+1;
		end
		if (in_x[0] == 1) b = ~b + 1;
		{c[0], s[0]} = a[0]+b[0];
		{c[1], s[1]} = a[1]+b[1]+c[0];
		{c[2], s[2]} = a[2]+b[2]+c[1];
		{c[3], s[3]} = a[3]+b[3]+c[2];
		if (((in_x[0]==0)&&(in_x[4]==in_x[8])&&(in_x[4]!=s[3]))||((in_x[0]==1)&&(in_x[4]!=in_x[8])&&(in_x[4]!=s[3])))
			out_c[1] = 1; 
		else out_c[1] = 0;//溢出
		out_c[2] = c[3];//最高进位
		out_c[0] = s[0]||s[1]||s[2]; //不管第一位符号为
		if ((s[3]==1)&&(out_c[1]==0))
			begin
				s = ~s+1;
				neg = 1;
			end
		else
			neg = 0;
		//七段译码
		case(s[2:0])
			0: SEGS = 7'b0111111;
			1: SEGS = 7'b0000110;
			2: SEGS = 7'b1011011;
			3: SEGS = 7'b1001111;
			4: SEGS = 7'b1100110;
			5: SEGS = 7'b1101101;
			6: SEGS = 7'b1111101;
			7: SEGS = 7'b0000111;
			default SEGS = 7'bx;
		endcase
		SEGS = ~SEGS;
		neg = ~neg;
	end
endmodule