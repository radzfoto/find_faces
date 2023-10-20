use std::path::{Path, PathBuf};
use std::fs;
use glob::Pattern;
use std::vec::IntoIter;

pub struct Traverser {
    root_dir: PathBuf,
    match_dirs: Vec<String>,
    match_files: Vec<String>,
    ignore_hidden: bool,
    ignore_list: Vec<String>,
    is_dir_iterator: bool,
    is_file_iterator: bool,
    current_dir: Option<PathBuf>,
    directories: IntoIter<PathBuf>,
    files_in_current_dir: IntoIter<PathBuf>,
}

impl Traverser {
    pub fn new(root_dir: PathBuf) -> Traverser {
        Traverser {
            root_dir: root_dir.clone(),
            match_dirs: vec!["*".to_string()],
            match_files: vec!["*".to_string()],
            ignore_hidden: true,
            ignore_list: vec![".DS_Store".to_string(), ".Trash".to_string()],
            is_dir_iterator: true,
            is_file_iterator: true,
            current_dir: None,
            directories: vec![root_dir].into_iter(),
            files_in_current_dir: vec![].into_iter(),
        }
    }

    fn get_next_dir(&mut self) -> Option<PathBuf> {
        while let Some(dir) = self.directories.next() {
            self.current_dir = Some(dir.clone());
            if self.is_dir_iterator && self.match_dir(&dir) {
                return Some(dir);
            }
        }
        None
    }

    fn match_dir(&self, path: &PathBuf) -> bool {
        let is_hidden = path.file_name().unwrap().to_str().unwrap().starts_with(".");
        if self.ignore_hidden && is_hidden {
            return false;
        }

        for pattern in &self.match_dirs {
            if Pattern::new(pattern).unwrap().matches(path.to_str().unwrap()) {
                return true;
            }
        }
        false
    }

    fn get_next_file(&mut self) -> Option<PathBuf> {
        if let Some(current_dir) = &self.current_dir {
            let mut files_in_current_dir: Vec<PathBuf> = vec![];
            for entry in fs::read_dir(current_dir).unwrap() {
                let entry = entry.unwrap();
                let path = entry.path();
                if path.is_file() && self.match_file(&path) {
                    files_in_current_dir.push(path);
                }
            }
            self.files_in_current_dir = files_in_current_dir.into_iter();
        }

        self.files_in_current_dir.next()
    }

    fn match_file(&self, path: &PathBuf) -> bool {
        let is_hidden = path.file_name().unwrap().to_str().unwrap().starts_with(".");
        if self.ignore_hidden && is_hidden {
            return false;
        }

        for pattern in &self.match_files {
            if Pattern::new(pattern).unwrap().matches(path.to_str().unwrap()) {
                return true;
            }
        }
        false
    }
}

impl Iterator for Traverser {
    type Item = PathBuf;

    fn next(&mut self) -> Option<Self::Item> {
        if self.is_dir_iterator && !self.is_file_iterator {
            return self.get_next_dir();
        } else if !self.is_dir_iterator && self.is_file_iterator {
            return self.get_next_file();
        } else if self.is_dir_iterator && self.is_file_iterator {
            if let Some(file) = self.get_next_file() {
                return Some(file);
            }
            return self.get_next_dir();
        }

        None
    }
}

fn main() {
    let mut traverser = Traverser::new(PathBuf::from("."));
    for path in traverser {
        println!("{}", path.display());
    }
}
