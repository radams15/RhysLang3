fn main() -> int {
    var file_name: str = "out.txt";

    var fd: int = fopen(file_name, 'w');

    fwrite(fd, "hello world\nthis is a text file!");

    fclose(fd);

    printf("%d\n", strlen("hello"));

    return 1;
}