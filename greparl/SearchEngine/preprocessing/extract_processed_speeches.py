from concurrent.futures import ProcessPoolExecutor
from functools import partial
from .funcs import process_csv_line, process_raw_speech_text


def process_line(this_line, do_stemming=False, remove_stopwords=False):
    """
    Given a line from the CSV file, gets the stemmed tokens.
    """
    speech = process_csv_line(this_line)
    speech_tokens = process_raw_speech_text(speech.contents, perform_stemming=do_stemming,
                                            delete_stopwords=remove_stopwords)
    return speech_tokens


def extract_processed_speeches(input_file_name: str, output_file_name: str, batch_size=20000, do_stemming=False,
                               remove_stopwords=False, limit=2000):
    """
    Creates a new file where each speech in the input file corresponds to its processed version in the output file.
    There is 1-1 line correspondence between the input file and the output file lines. (i.e. speech at line 1000
    in the input file, has its processed contents in line 1000 at the output file)
    :param batch_size How many lines will be processes at once. Affects memory usage
    :param do_stemming Whether to stem the words
    :param remove_stopwords Whether to remove stopwords from the processed text
    :param limit extract the first limit speeches from the file. If -1 extract all speeches
    """

    # Execute the tasks in parallel
    executor = ProcessPoolExecutor(max_workers=4)
    futures = []
    input_file = open(input_file_name, "r", encoding='utf8')
    output_file = open(output_file_name, "w", encoding='utf8')
    # Ignore the first line
    input_file.readline()
    # Add an empty line corresponding to the first line of the speeches csv
    output_file.write("\n")
    # Create the process line function using the provided arguments
    func_with_args = partial(process_line, do_stemming=do_stemming, remove_stopwords=remove_stopwords)
    # Read batch_sized lines at each iteration until EOF
    # https://stackoverflow.com/questions/34770169/using-concurrent-futures-without-running-out-of-ram
    read = 0
    while (line := input_file.readline()) and (limit == -1 or read < limit):
        futures.append(executor.submit(func_with_args, line))
        read += 1
        # Job queue is full, process all jobs and empty the queue
        if len(futures) >= batch_size:
            for future in futures:
                processed_line = future.result()
                output_file.write(' '.join(processed_line))
                output_file.write("\n")
            futures.clear()
    # Process remaining lines
    for future in futures:
        processed_line = future.result()
        output_file.write(' '.join(processed_line))
        output_file.write("\n")
    futures.clear()
