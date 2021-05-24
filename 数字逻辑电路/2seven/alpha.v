module alpha(en,x,y,z,A,B,C,D,E,F,G);
	input [7:0] x;
	input en;
	output reg [2:0]y;
	output reg z;
	output reg A,B,C,D,E,F,G;
	reg [1:7] SEGS;
	integer k,i;
	
	
	always @(x or en)
	if (en)
	begin
		y = 0;
		k = 0;
		for (i=0;i<=7;i = i+1)
			if(x[i]==1)
			   begin
				y = i;
				k = 1;
				end
		if (k==0) 
			z = 1'd0;
		else 
			z = 1'd1;
		
		if (z==1)
			begin
			case(y+1)
				1: SEGS = 7'b0110000;
				2: SEGS = 7'b1101101;
				3: SEGS = 7'b1111001;
				4: SEGS = 7'b0110011;
				5: SEGS = 7'b1011011;
				6: SEGS = 7'b0011111;
				7: SEGS = 7'b1110000;
				8: SEGS = 7'b1111111;
				9: SEGS = 7'b1110011;
				default SEGS = 7'bx;
			endcase
			end
		else
			SEGS = 7'b1111110;
		{A,B,C,D,E,F,G} = ~SEGS;
   end
	else
	begin
     {A,B,C,D,E,F,G} = 7'b1111111;
	  y = 3'b000;
	  z = 1'b0;
	end
endmodule
