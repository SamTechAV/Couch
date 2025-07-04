#!/usr/bin/env python3
"""
Tree-based GUI Git/AI Digest Ignore Manager
Allows you to select files and directories in a tree view to add to .gitignore and .aidigestignore
"""

import os
import sys
import fnmatch
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
from typing import List, Set, Tuple, Dict


class IgnoreManagerTreeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Git/AI Digest Ignore Manager - Tree View")
        self.root.geometry("1000x750")

        # Variables
        self.directory = tk.StringVar(value=os.getcwd())
        self.tree_items = {}  # Dict to store tree item IDs and their data

        self.setup_ui()
        self.refresh_tree()

    def setup_ui(self):
        """Create the GUI layout"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)

        # Directory selection
        dir_frame = ttk.LabelFrame(main_frame, text="Directory", padding="5")
        dir_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        dir_frame.columnconfigure(1, weight=1)

        ttk.Label(dir_frame, text="Working Directory:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        dir_entry = ttk.Entry(dir_frame, textvariable=self.directory, width=50)
        dir_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(dir_frame, text="Browse", command=self.browse_directory).grid(row=0, column=2)
        ttk.Button(dir_frame, text="Refresh", command=self.refresh_tree).grid(row=0, column=3, padx=(5, 0))

        # Tree frame
        tree_frame = ttk.LabelFrame(main_frame, text="Files and Directories", padding="5")
        tree_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(2, weight=1)

        # Selection buttons
        select_frame = ttk.Frame(tree_frame)
        select_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))

        ttk.Button(select_frame, text="Check All", command=self.check_all).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(select_frame, text="Uncheck All", command=self.uncheck_all).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(select_frame, text="Check Files Only", command=self.check_files_only).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(select_frame, text="Check Dirs Only", command=self.check_dirs_only).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(select_frame, text="Expand All", command=self.expand_all).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(select_frame, text="Collapse All", command=self.collapse_all).pack(side=tk.LEFT)

        # Search frame
        search_frame = ttk.Frame(tree_frame)
        search_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        search_frame.columnconfigure(1, weight=1)

        ttk.Label(search_frame, text="Filter:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_tree)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(search_frame, text="Clear", command=self.clear_filter).grid(row=0, column=2)

        # Create treeview with checkboxes
        tree_container = ttk.Frame(tree_frame)
        tree_container.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_container.columnconfigure(0, weight=1)
        tree_container.rowconfigure(0, weight=1)

        # Configure treeview columns
        self.tree = ttk.Treeview(tree_container, columns=('type', 'size'), show='tree headings')
        self.tree.heading('#0', text='Name', anchor=tk.W)
        self.tree.heading('type', text='Type', anchor=tk.W)
        self.tree.heading('size', text='Size', anchor=tk.E)

        self.tree.column('#0', width=400, minwidth=200)
        self.tree.column('type', width=80, minwidth=50)
        self.tree.column('size', width=100, minwidth=60)

        # Scrollbars for tree
        tree_scroll_y = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.tree.yview)
        tree_scroll_x = ttk.Scrollbar(tree_container, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)

        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_scroll_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        tree_scroll_x.grid(row=1, column=0, sticky=(tk.W, tk.E))

        # Bind tree events
        self.tree.bind('<Button-1>', self.on_tree_click)
        self.tree.bind('<space>', self.on_tree_space)

        # Configure tags for different item types
        self.tree.tag_configure('checked', foreground='blue')
        self.tree.tag_configure('unchecked', foreground='black')
        self.tree.tag_configure('directory', foreground='darkblue')
        self.tree.tag_configure('file', foreground='darkgreen')

        # Action frame
        action_frame = ttk.LabelFrame(main_frame, text="Actions", padding="5")
        action_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        # Ignore file options
        ignore_frame = ttk.Frame(action_frame)
        ignore_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(ignore_frame, text="Add selected items to:").pack(side=tk.LEFT, padx=(0, 10))

        self.gitignore_var = tk.BooleanVar(value=True)
        self.aidigest_var = tk.BooleanVar(value=False)

        ttk.Checkbutton(ignore_frame, text=".gitignore", variable=self.gitignore_var).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Checkbutton(ignore_frame, text=".aidigestignore", variable=self.aidigest_var).pack(side=tk.LEFT)

        # Action buttons
        button_frame = ttk.Frame(action_frame)
        button_frame.pack(fill=tk.X)

        ttk.Button(button_frame, text="Add to Ignore Files", command=self.add_to_ignore_files).pack(side=tk.LEFT,
                                                                                                    padx=(0, 5))
        ttk.Button(button_frame, text="Preview Changes", command=self.preview_changes).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="View Ignore Files", command=self.view_ignore_files).pack(side=tk.LEFT,
                                                                                                padx=(0, 5))

        # Selection info
        self.selection_var = tk.StringVar(value="0 items selected")
        ttk.Label(button_frame, textvariable=self.selection_var).pack(side=tk.RIGHT, padx=(10, 0))

        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(10, 0))

    def browse_directory(self):
        """Open directory browser"""
        directory = filedialog.askdirectory(initialdir=self.directory.get())
        if directory:
            self.directory.set(directory)
            self.refresh_tree()

    def get_existing_patterns(self, ignore_file: Path) -> Set[str]:
        """Read existing patterns from ignore file"""
        if not ignore_file.exists():
            return set()

        patterns = set()
        try:
            with open(ignore_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        patterns.add(line)
        except Exception as e:
            self.status_var.set(f"Warning: Could not read {ignore_file}: {e}")

        return patterns

    def is_ignored(self, path_str: str, git_patterns: Set[str], ai_patterns: Set[str]) -> bool:
        """Check if path matches any existing ignore patterns"""
        for pattern in git_patterns | ai_patterns:
            if fnmatch.fnmatch(path_str, pattern) or fnmatch.fnmatch(os.path.basename(path_str), pattern):
                return True
        return False

    def get_file_size(self, file_path: Path) -> str:
        """Get human-readable file size"""
        try:
            if file_path.is_file():
                size = file_path.stat().st_size
                for unit in ['B', 'KB', 'MB', 'GB']:
                    if size < 1024.0:
                        return f"{size:.1f} {unit}"
                    size /= 1024.0
                return f"{size:.1f} TB"
            else:
                return "Folder"
        except:
            return "Unknown"

    def populate_tree(self, parent_item: str, directory: Path, relative_path: str = ""):
        """Recursively populate the tree"""
        try:
            items = []

            # Get all items in directory
            for item in directory.iterdir():
                if item.name.startswith('.') and item.name not in ['.gitignore', '.aidigestignore']:
                    continue  # Skip hidden files except ignore files

                item_rel_path = os.path.join(relative_path, item.name) if relative_path else item.name

                # Check if ignored
                gitignore_path = Path(self.directory.get()) / ".gitignore"
                aidigestignore_path = Path(self.directory.get()) / ".aidigestignore"
                git_patterns = self.get_existing_patterns(gitignore_path)
                ai_patterns = self.get_existing_patterns(aidigestignore_path)

                if item.is_dir():
                    if not self.is_ignored(item_rel_path + "/", git_patterns, ai_patterns):
                        items.append((item, item_rel_path + "/", True))
                else:
                    if not self.is_ignored(item_rel_path, git_patterns, ai_patterns):
                        items.append((item, item_rel_path, False))

            # Sort items: directories first, then files
            items.sort(key=lambda x: (not x[2], x[0].name.lower()))

            for item_path, rel_path, is_dir in items:
                # Determine icon and type
                if is_dir:
                    icon = "📁"
                    item_type = "Folder"
                    tags = ('directory', 'unchecked')
                else:
                    icon = "📄"
                    item_type = "File"
                    tags = ('file', 'unchecked')

                # Get size
                size = self.get_file_size(item_path)

                # Insert item into tree
                item_id = self.tree.insert(parent_item, tk.END,
                                           text=f"☐ {icon} {item_path.name}",
                                           values=(item_type, size),
                                           tags=tags,
                                           open=False)

                # Store item data
                self.tree_items[item_id] = {
                    'path': rel_path,
                    'is_dir': is_dir,
                    'checked': False,
                    'full_path': item_path
                }

                # Recursively populate subdirectories
                if is_dir and item_path.is_dir():
                    try:
                        # Check if directory has any non-ignored children
                        has_children = False
                        for child in item_path.iterdir():
                            if not child.name.startswith('.') or child.name in ['.gitignore', '.aidigestignore']:
                                child_rel = os.path.join(rel_path,
                                                         child.name) if rel_path != item_path.name + "/" else child.name
                                if child.is_dir():
                                    if not self.is_ignored(child_rel + "/", git_patterns, ai_patterns):
                                        has_children = True
                                        break
                                else:
                                    if not self.is_ignored(child_rel, git_patterns, ai_patterns):
                                        has_children = True
                                        break

                        if has_children:
                            self.populate_tree(item_id, item_path, rel_path)
                    except PermissionError:
                        # Add a placeholder for permission denied directories
                        placeholder_id = self.tree.insert(item_id, tk.END,
                                                          text="🔒 Permission Denied",
                                                          values=("", ""),
                                                          tags=('disabled',))

        except PermissionError:
            pass  # Skip directories we can't access
        except Exception as e:
            self.status_var.set(f"Error populating tree: {e}")

    def refresh_tree(self):
        """Refresh the entire tree"""
        self.status_var.set("Refreshing tree...")

        # Clear existing tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.tree_items.clear()

        # Get directory
        directory = Path(self.directory.get())
        if not directory.exists():
            self.status_var.set("Directory does not exist")
            return

        # Populate tree
        self.populate_tree("", directory)

        # Update status
        total_items = len(self.tree_items)
        self.status_var.set(f"Loaded {total_items} items")
        self.update_selection_count()

    def on_tree_click(self, event):
        """Handle tree item clicks"""
        item = self.tree.identify('item', event.x, event.y)
        if item and item in self.tree_items:
            # Check if click was on the checkbox area (approximate)
            region = self.tree.identify_region(event.x, event.y)
            if region == "tree":
                self.toggle_item(item)

    def on_tree_space(self, event):
        """Handle spacebar press on tree items"""
        selection = self.tree.selection()
        if selection:
            for item in selection:
                if item in self.tree_items:
                    self.toggle_item(item)

    def toggle_item(self, item_id):
        """Toggle the checked state of an item"""
        if item_id not in self.tree_items:
            return

        item_data = self.tree_items[item_id]
        item_data['checked'] = not item_data['checked']

        # Update visual representation
        current_text = self.tree.item(item_id, 'text')
        if item_data['checked']:
            new_text = current_text.replace('☐', '☑')
            tags = list(self.tree.item(item_id, 'tags'))
            tags = [tag for tag in tags if tag not in ['unchecked']]
            tags.append('checked')
        else:
            new_text = current_text.replace('☑', '☐')
            tags = list(self.tree.item(item_id, 'tags'))
            tags = [tag for tag in tags if tag not in ['checked']]
            tags.append('unchecked')

        self.tree.item(item_id, text=new_text, tags=tags)
        self.update_selection_count()

    def check_all(self):
        """Check all items"""
        for item_id in self.tree_items:
            if not self.tree_items[item_id]['checked']:
                self.toggle_item(item_id)

    def uncheck_all(self):
        """Uncheck all items"""
        for item_id in self.tree_items:
            if self.tree_items[item_id]['checked']:
                self.toggle_item(item_id)

    def check_files_only(self):
        """Check only files"""
        for item_id, item_data in self.tree_items.items():
            should_be_checked = not item_data['is_dir']
            if item_data['checked'] != should_be_checked:
                self.toggle_item(item_id)

    def check_dirs_only(self):
        """Check only directories"""
        for item_id, item_data in self.tree_items.items():
            should_be_checked = item_data['is_dir']
            if item_data['checked'] != should_be_checked:
                self.toggle_item(item_id)

    def expand_all(self):
        """Expand all tree items"""

        def expand_children(item):
            self.tree.item(item, open=True)
            for child in self.tree.get_children(item):
                expand_children(child)

        for item in self.tree.get_children():
            expand_children(item)

    def collapse_all(self):
        """Collapse all tree items"""

        def collapse_children(item):
            self.tree.item(item, open=False)
            for child in self.tree.get_children(item):
                collapse_children(child)

        for item in self.tree.get_children():
            collapse_children(item)

    def filter_tree(self, *args):
        """Filter tree items based on search text"""
        search_text = self.search_var.get().lower()

        def filter_item(item_id):
            item_data = self.tree_items.get(item_id)
            if not item_data:
                return False

            # Check if item matches search
            item_name = item_data['full_path'].name.lower()
            matches = search_text in item_name if search_text else True

            # Check children
            children = self.tree.get_children(item_id)
            child_matches = any(filter_item(child) for child in children)

            # Show item if it matches or has matching children
            show = matches or child_matches

            # Hide/show item (this is a simplified approach)
            # In a real implementation, you might want to rebuild the tree

            return show

        # For now, just expand items that match the search
        if search_text:
            for item_id in self.tree_items:
                item_data = self.tree_items[item_id]
                if search_text in item_data['full_path'].name.lower():
                    # Expand parent items
                    parent = self.tree.parent(item_id)
                    while parent:
                        self.tree.item(parent, open=True)
                        parent = self.tree.parent(parent)

    def clear_filter(self):
        """Clear the search filter"""
        self.search_var.set("")
        self.collapse_all()

    def update_selection_count(self):
        """Update the selection count display"""
        checked_count = sum(1 for item_data in self.tree_items.values() if item_data['checked'])
        self.selection_var.set(f"{checked_count} items selected")

    def get_selected_files(self) -> List[str]:
        """Get list of selected file paths"""
        return [item_data['path'] for item_data in self.tree_items.values() if item_data['checked']]

    def preview_changes(self):
        """Preview what will be added to ignore files"""
        selected = self.get_selected_files()
        if not selected:
            messagebox.showwarning("No Selection", "Please select files to preview.")
            return

        git_selected = self.gitignore_var.get()
        ai_selected = self.aidigest_var.get()

        if not git_selected and not ai_selected:
            messagebox.showwarning("No Target", "Please select at least one ignore file.")
            return

        # Create preview window
        preview_window = tk.Toplevel(self.root)
        preview_window.title("Preview Changes")
        preview_window.geometry("600x400")

        # Create notebook for tabs
        notebook = ttk.Notebook(preview_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        if git_selected:
            git_frame = ttk.Frame(notebook)
            notebook.add(git_frame, text=".gitignore")

            git_text = scrolledtext.ScrolledText(git_frame, wrap=tk.WORD)
            git_text.pack(fill=tk.BOTH, expand=True)
            git_text.insert(tk.END, "# Files to be added to .gitignore:\n\n")
            for path in sorted(selected):
                git_text.insert(tk.END, f"{path}\n")

        if ai_selected:
            ai_frame = ttk.Frame(notebook)
            notebook.add(ai_frame, text=".aidigestignore")

            ai_text = scrolledtext.ScrolledText(ai_frame, wrap=tk.WORD)
            ai_text.pack(fill=tk.BOTH, expand=True)
            ai_text.insert(tk.END, "# Files to be added to .aidigestignore:\n\n")
            for path in sorted(selected):
                ai_text.insert(tk.END, f"{path}\n")

    def add_to_ignore_file(self, ignore_file: Path, patterns: List[str]) -> bool:
        """Add patterns to ignore file"""
        if not patterns:
            return True

        existing = self.get_existing_patterns(ignore_file)
        new_patterns = [p for p in patterns if p not in existing]

        if not new_patterns:
            return True  # All patterns already exist

        try:
            # Create file if it doesn't exist
            if not ignore_file.exists():
                ignore_file.touch()

            with open(ignore_file, 'a', encoding='utf-8') as f:
                # Add newline if file doesn't end with one
                if ignore_file.stat().st_size > 0:
                    with open(ignore_file, 'r', encoding='utf-8') as rf:
                        content = rf.read()
                        if not content.endswith('\n'):
                            f.write('\n')

                # Add comment
                f.write(f'\n# Added by ignore manager\n')

                # Add patterns
                for pattern in new_patterns:
                    f.write(f'{pattern}\n')

            return True

        except Exception as e:
            messagebox.showerror("Error", f"Error writing to {ignore_file}: {e}")
            return False

    def add_to_ignore_files(self):
        """Add selected files to ignore files"""
        selected = self.get_selected_files()
        if not selected:
            messagebox.showwarning("No Selection", "Please select files to add.")
            return

        git_selected = self.gitignore_var.get()
        ai_selected = self.aidigest_var.get()

        if not git_selected and not ai_selected:
            messagebox.showwarning("No Target", "Please select at least one ignore file.")
            return

        directory = Path(self.directory.get())
        success = True
        messages = []

        if git_selected:
            gitignore_path = directory / ".gitignore"
            existing = self.get_existing_patterns(gitignore_path)
            new_patterns = [p for p in selected if p not in existing]

            if self.add_to_ignore_file(gitignore_path, selected):
                if new_patterns:
                    messages.append(f"Added {len(new_patterns)} patterns to .gitignore")
                else:
                    messages.append("All patterns already exist in .gitignore")
            else:
                success = False

        if ai_selected:
            aidigest_path = directory / ".aidigestignore"
            existing = self.get_existing_patterns(aidigest_path)
            new_patterns = [p for p in selected if p not in existing]

            if self.add_to_ignore_file(aidigest_path, selected):
                if new_patterns:
                    messages.append(f"Added {len(new_patterns)} patterns to .aidigestignore")
                else:
                    messages.append("All patterns already exist in .aidigestignore")
            else:
                success = False

        if success:
            messagebox.showinfo("Success", "\n".join(messages))
            self.uncheck_all()
            self.refresh_tree()  # Refresh to remove newly ignored files
        else:
            messagebox.showerror("Error", "Some errors occurred while updating files.")

    def view_ignore_files(self):
        """View contents of ignore files"""
        directory = Path(self.directory.get())
        gitignore_path = directory / ".gitignore"
        aidigest_path = directory / ".aidigestignore"

        # Create viewer window
        viewer_window = tk.Toplevel(self.root)
        viewer_window.title("View Ignore Files")
        viewer_window.geometry("700x500")

        # Create notebook for tabs
        notebook = ttk.Notebook(viewer_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # .gitignore tab
        git_frame = ttk.Frame(notebook)
        notebook.add(git_frame, text=".gitignore")

        git_text = scrolledtext.ScrolledText(git_frame, wrap=tk.WORD)
        git_text.pack(fill=tk.BOTH, expand=True)

        if gitignore_path.exists():
            try:
                with open(gitignore_path, 'r', encoding='utf-8') as f:
                    git_text.insert(tk.END, f.read())
            except Exception as e:
                git_text.insert(tk.END, f"Error reading .gitignore: {e}")
        else:
            git_text.insert(tk.END, ".gitignore file does not exist")

        # .aidigestignore tab
        ai_frame = ttk.Frame(notebook)
        notebook.add(ai_frame, text=".aidigestignore")

        ai_text = scrolledtext.ScrolledText(ai_frame, wrap=tk.WORD)
        ai_text.pack(fill=tk.BOTH, expand=True)

        if aidigest_path.exists():
            try:
                with open(aidigest_path, 'r', encoding='utf-8') as f:
                    ai_text.insert(tk.END, f.read())
            except Exception as e:
                ai_text.insert(tk.END, f"Error reading .aidigestignore: {e}")
        else:
            ai_text.insert(tk.END, ".aidigestignore file does not exist")


def main():
    """Main entry point"""
    root = tk.Tk()
    app = IgnoreManagerTreeGUI(root)

    # Center window on screen
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")

    try:
        root.mainloop()
    except KeyboardInterrupt:
        root.quit()


if __name__ == "__main__":
    main()