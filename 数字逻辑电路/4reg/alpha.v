module alpha(en,i,o,clk,set);
	input [2:0] en;
	input clk,i;
	input [5:0] set;
	output reg [5:0] o;
	
	
	always @(posedge clk) 
		begin
		if (en == 3'b000)
			o <= 6'b000000;
		else if (en==3'b001) 
			o<=set;
		else if (en==3'b010)
			o<={1'b0,o[5:1]};
		else if (en==3'b011)
			o<={o[4:0],1'b0};
		else if (en==3'b100)
			o<={o[5],o[5:1]};
		else if(en==3'b101)
			begin
			o<={o[4:0],i};
			end
		else if(en==3'b110)
			o<={o[0],o[5:1]};
		else
			o<={o[4:0],o[5]};
		end
endmodule
