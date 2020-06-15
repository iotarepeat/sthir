import spectral_bloom_filter
import parse
import convert_2p15
import base64
import glob
from bitarray import bitarray
from generate_search import base2p15_encode

def get_all_html_files(directory):
    return glob.glob("./*.html")

def get_all_bin_files(directory):
    return glob.glob("./*.bin")

def generate_bloom_filter(file, false_positive=0.1, chunk_size=4):
    spectral = spectral_bloom_filter.Spectral_Bloom_Filter()
    tokens = parse.extract_html_bs4(file)

    no_items = len(tokens)
    m, k = spectral.optimal_m_k(no_items, false_positive)
    spectral.create_filter(tokens, m, 
                            chunk_size, k, 
                            to_bitarray=True, 
                            bitarray_path=file.replace(".html", ".bin"))
    return {
        "m": m,
        "k": k,
        "chunk_size": chunk_size,
        "bin_file": file.replace(".html", ".bin")
    }

def create_search_page(directory):
    files = get_all_html_files(directory)
    bloom_meta = list()
    for file in files:
        bloom_meta.append(generate_bloom_filter(file))

    base2p15_arrs = list()
    for document in bloom_meta:
        bit_arr = bitarray()
        with open(document["bin_file"], "rb") as f:
            bit_arr.fromfile(f)

        base2p15_arrs.append([base2p15_encode(bit_arr.to01()), 
                                document["chunk_size"], 
                                document["m"], 
                                document["k"], document["bin_file"]])
        print("Scanned: {}".format(document["bin_file"]))

    with open("output_2p15.html", "w") as f:
        f.write(convert_2p15.HTML_TEMPLATE["HEAD"])
        f.write(convert_2p15.HTML_TEMPLATE["TAIL"].format(base2p15_arrs))

if __name__ == "__main__":
    create_search_page("./")