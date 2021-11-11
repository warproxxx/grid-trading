## Instruction:
1) ssh into the server
2) screen -r -d grid
![Screenshot](ss.png)

Sample Input:
python3 script.py --divNumber 10 —maxOrder 100 —orderAbove 50 —orderBelow 50 —startPrice 59995 --sleepTime 60

If —startPrice is not set or set to -1, current price will be used

To detach:
3) Ctrl A + d