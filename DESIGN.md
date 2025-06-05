# PowerMake 

# Description:

An enhanced version of a makefile style workflow manager.

# What it does:

- It reads a _pipeline_ spec from a yaml file
- It executes each step and produces one or more files as a result

# Example yml spec 

```
- node: readfile 
  path: /home/coco/example.csv # file is read and copied to a tmp file in a tmp dir
  id  : examplecsv

- node: runscript
  path: cocoliso.sh ${examplecsv} # node ids are expanded to the path of the tmp file
  # runscript nodes should send their output to stdout and powermake should redirect this to a tmp file and keep record so the id can be used as input for follwowing nodes
  id  : cocoliso 

- node: writefile
  # writefile nodes read the tmp file pointed by the input id , and copy the output to the specified output place
  input : cocoliso
  output: /home/myresult.txt
```

# What is expected from v1

- Read the pipeline spec yml file name from cli. Use the typer library for this.
- Set reasonable defaults for the tmp dir where tmp files are kept (say .tmp/ in the sampe dir where the pipeline spec is stored), allow a cli parameter to override this default
- Display progress information
  - Display current node being run, display total node count
  - Display time spent so far
- Through sanity checking.
  - Syntax check the pipeline spec
  - All nodes where specific paths are specified by the user (input files, script paths) should be checked for existence before trying to run the spec.
  - Rich error messages, be explicit on what failed
- Provide some unit test coverage 

# What is specifically not expected in v1

- Calculate dependencies among nodes
- Parallel execution
