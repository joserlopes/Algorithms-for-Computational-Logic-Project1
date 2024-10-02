# Welcome to alc24\!


This git repository belongs to group 19 and is intended for project1 of alc24.


The project statement is available at [project_statement.pdf](project_statement.pdf).


Students must submit their solution to project1 here, which will be automatically evaluated using a set of holdout tests. The students do not have access to this set of tests.


The result of the project evaluation using this set of holdout tests will be available in the [README](https://gitlab.rnl.tecnico.ulisboa.pt/alc24/feedback/project1/19/-/tree/master/README.md) of the feedback repository after each code submission.


The overall performance of students in project1 using the set of holdout tests can be consulted in the [_dashboard_](https://gitlab.rnl.tecnico.ulisboa.pt/alc24/alc24/-/tree/master/dashboard/projects/project1.md) of the project, present in the global alc24 repository.



- **Important notes:**


  - Students should add their report (pdf) to the [report](report/) directory.


  - [+Students must wait 15 minute(s) between submissions+]. This way, you have to wait 15 minute(s) to resubmit their projects. Otherwise, the students' submission will not be evaluated.


  - [-Students cannot change the .gitlab-ci.yml file present in this repository-]. Changing this file will result in the student being unable to access this repository, there will be no exceptions.


  - [+The set of public tests available on your git repository is different from the set of holdout tests+] being used to evaluate your project on GitLab. Furthermore, [+after the project deadline your projects will be evaluated using another set of holdout tests+].


  - The script [+run.sh verifies whether your output achieves the optimal cost+], by comparing your output with the expected one.




- Running your project locally:


```
python3 project1.py < test1.ttp > test1.myout 
```


- To run the other scripts in the git repository, you need to unzip the ttp-checker executable. If you are using a MacOS system unzip the MacOS checker, otherwise if you are using a Linux system unzip the Linux checker. Run the following command:


```
unzip ttp-checker.zip; chmod +x ttp-checker
```


- To check your output for testX.ttp run:


```
./ttp-checker testX.ttp testX.myout
```



- To evaluate all the public tests locally on your PC, run:


```
chmod +x run.sh
./run.sh
```




- Most common assessment results for each test:


  - _Accepted_ : The result of the program is as expected.


  - _Wrong Answer_ : The result of the program is different from what was expected.


  - _Presentation Error_ : Program result differs from expected in blank spaces or blank lines.


  - _Compile Time Error_ : A compilation error occurred while compiling the program.


  - _Time Limit Exceeded_ : The program program execution time has exceeded the allowed time.


  - _Memory Limit Exceeded_ : Program execution memory exceeded the allowed memory.


  - _Output Limit Exceeded_ : The program execution output exceeded the allowed space.


  - Others : An error occurred during the execution of the program which caused the program to stop unexpectedly.


