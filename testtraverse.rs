#[cfg(test)]
mod tests {
    use super::*;
    use std::path::Path;
    use std::collections::HashSet;
    use tempfile::tempdir;

    #[test]
    fn test_traverse_only_dirs() {
        let dir = tempdir().unwrap();
        let root = dir.path().to_owned();
        create_test_dir_tree(&root);
        
        let mut traverser = Traverser::new(root.clone());
        traverser.is_dir_iterator = true;
        traverser.is_file_iterator = false;
        
        let mut actual_dirs: HashSet<PathBuf> = HashSet::new();
        for dir in traverser {
            actual_dirs.insert(dir);
        }

        let expected_dirs: HashSet<PathBuf> = [
            root.join("dir1"),
            root.join("dir2"),
            root.join("dir2/dir2_1"),
            root.join("dir2/dir2_2"),
            root.join(".dir3"),
            root.join(".dir4"),
            root.join("dir2/.dir2_3"),
            root.clone(),
        ].iter().cloned().collect();

        assert_eq!(expected_dirs, actual_dirs);
    }

    // Implement other test functions...

    fn create_test_dir_tree(root: &Path) {
        let mut dir_tree = vec![
            (root.join("dir1"), vec!["file1_1", "file1_2", "file_1_3", ".file1_4", ".file1_5"]),
            (root.join("dir2/dir2_1"), vec!["file2_1"]),
            (root.join(".dir4"), vec![".file4_1"]),
        ];

        std::fs::create_dir_all(root).unwrap();
        for (dir, files) in dir_tree.iter_mut() {
            std::fs::create_dir_all(dir).unwrap();
            for file in files.iter() {
                let path = dir.join(file);
                std::fs::write(&path, "Some text").unwrap();
            }
        }
    }
}
