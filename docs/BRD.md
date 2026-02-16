# Business Requirements Document (BRD)

I want to create python application.
This application will have two entry points: a command-line interface (CLI) and MCP (model context protocol) server. The application will be designed to handle various tasks related to operations with file system. The CLI will allow users to interact with the application through terminal commands, while the MCP server will enable communication with AI models.

File system operations will include:
1. **Create Files**: Allowing to create one or more new files with specified names and content.
2. **Read Files**: Allowing to read the content of one or more existing files.
3. **Update Files**: Allowing to modify the content of one or more existing files.
4. **Delete Files**: Allowing to delete one or more existing files.
5. **File Search**: Searching for files based on name, type, or content.
6. **Copy or Move Files**: Allowing to copy or move one or more existing files to a specified locations.

7. **Create Directories**: Allowing to create one or more new directories with specified names.
8. **Read Directories**: Allowing to list the contents of one or more existing directories.
9. **Update Directories**: Allowing to rename or move one or more existing directories.
10. **Delete Directories**: Allowing to delete one or more existing directories.
11. **Directory Search**: Searching for directories based on name or content.
12. **Copy or Move Directories**: Allowing to copy or move one or more existing directories to a specified locations.

13. **File SystemOutline**: Generating an outline of the file system structure, showing directories and files in a hierarchical format. This will help users visualize the organization of their files and directories. The outline will include details such as file sizes, types, and modification dates, providing a comprehensive overview of the file system. Users can specify the depth of the outline to focus on specific levels of the directory structure.
14. **Files Outline**: Generating an outline of the specified files. This will provide users with a detailed view of the selected files. For MD files, the outline will include the structure of the document, such as headings, subheadings, start and end lines of each section. For python files, the outline will include the structure of the code, such as file level docstring, classes, functions, their respective line numbers and docstrings.