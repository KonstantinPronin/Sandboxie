
#include <iostream>
#include <windows.h>

int main()
{
    srand((unsigned)time(NULL));
    POINT oldPos;
    POINT curPos;

    GetCursorPos(&oldPos);
    while (true) {
        GetCursorPos(&curPos);

        if (oldPos.x == curPos.x && oldPos.y == curPos.y) {
            int x = rand() % 100;
            int y = rand() % 100;
            SetCursorPos(x, y);
            oldPos.x = x;
            oldPos.y = y;
        }

        Sleep(1000);
    }
}