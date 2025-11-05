#ifndef FIVM_CSVREADER_HPP
#define FIVM_CSVREADER_HPP

#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <typeinfo>

using namespace std;

class CSVAdaptor {
    public:
        CSVAdaptor(char del) : delimiter(del) { }

        std::string const& operator[](std::size_t index) const {
            return data[index];
        }

        std::size_t size() const {
            return data.size();
        }

        void readNextRow(std::istream& str) {
            data.clear();

            std::string line;
            std::getline(str, line);

            std::stringstream lineStream(line);
            std::string cell;

            while (std::getline(lineStream, cell, delimiter)) {
                /* std::cout << cell << std::endl; */
                // FIXME: this is a hack to handle empty cells
                if (cell.empty()) {
                    data.push_back("-1");
                } else {
                    data.push_back(cell);
                }
                // data.push_back(cell);
            }

            // FIXME: handle empty cells at the end of the line
            if (line.back() == delimiter) {
                data.push_back("-1");
            }
        }

        std::vector<std::string> data;

    private:
        char delimiter;
};

std::istream& operator>>(std::istream& str, CSVAdaptor& data) {
    data.readNextRow(str);
    return str;
}

template <typename T>
void readFromFile(std::vector<T>& data, const std::string& path, char delimiter) {
    data.clear();

    std::ifstream file(path);
    if (!file) {
        cerr << "ERROR: " << path << " doesn't exist" << endl;
        return;
    }

    CSVAdaptor row(delimiter);

    while (file >> row) {
        /* if (path.find("cast_info") != std::string::npos) { */
        /*     std::cout << "row.size() = " << row.size() << std::endl; */
        /*     for (size_t i = 0; i < row.size(); i++) { */
        /*         std::cout << row[i] << " "; */
        /*     } */
        /*     std::cout << std::endl; */
        /* } */

        T tmp(row.data, 1L);

        // if (path.find("movie_info_idx") != std::string::npos) {
        //     std::cout << "tmp created" << std::endl;
        // }
        data.push_back(tmp);
        // if (path.find("movie_info_idx") != std::string::npos) {
        //     std::cout << "tmp pushed" << std::endl;
        // }
    }

    file.close();
}

template <typename T>
void readFromBinaryFile(std::vector<T>& data, const std::string& path) {
    data.clear();

    std::ifstream file(path, std::ios::in | std::ios::binary);

    size_t length;
    file.read((char*) &length, sizeof(size_t));
    data.reserve(length);

    T tmp;
    for (size_t i = 0; i < length; i++) {
        tmp.readFrom(file);
        data.push_back(tmp);
    }

    file.close();
}

template <typename T>
void writeToBinaryFile(std::vector<T>& data, const std::string& path) {
    std::ofstream file(path, std::ios::out | std::ios::binary);

    size_t length = data.size();
    file.write((char*) &length, sizeof(size_t));
    for (T t : data) t.writeTo(file);

    file.close();
}

#endif /* FIVM_CSVREADER_HPP */
