import sys
import heapq
from collections import defaultdict
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget,
    QTextEdit, QFileDialog, QMessageBox, QRadioButton, QButtonGroup, QGraphicsScene,
    QGraphicsView, QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsTextItem, QScrollArea
)
from PyQt6.QtCore import Qt, QPointF


# Represents a single node in the Huffman Tree
class HuffmanNode:
    def __init__(self, char, freq):
        self.char = char  # Character represented by the node
        self.freq = freq  # Frequency of the character
        self.left = None  # Left child of the node
        self.right = None  # Right child of the node

    # Define comparison based on frequency for heap operations
    def __lt__(self, other):
        return self.freq < other.freq


# Implements the Huffman Coding algorithm
class HuffmanCoding:
    def __init__(self):
        self.codes = {}  # Stores the binary codes for each character
        self.reverse_mapping = {}  # Reverse mapping from codes to characters
        self.root = None  # Root of the Huffman Tree

    # Builds a frequency dictionary from the input text
    def build_frequency_dict(self, text):
        frequency = defaultdict(int)
        for char in text:
            frequency[char] += 1
        return frequency

    # Builds a min-heap based on character frequencies
    def build_heap(self, frequency):
        heap = []
        for char, freq in frequency.items():
            node = HuffmanNode(char, freq)
            heapq.heappush(heap, node)
        return heap

    # Merges nodes to build the Huffman Tree
    def merge_nodes(self, heap):
        while len(heap) > 1:
            node1 = heapq.heappop(heap)  # Node with the smallest frequency
            node2 = heapq.heappop(heap)  # Node with the second smallest frequency
            # Create a new merged node
            merged = HuffmanNode(None, node1.freq + node2.freq)
            merged.left = node1
            merged.right = node2
            heapq.heappush(heap, merged)  # Push the merged node back into the heap
        self.root = heap[0]
        return self.root

    # Recursive helper to generate Huffman codes
    def build_codes_helper(self, root, current_code):
        if root is None:
            return
        # If a leaf node, assign the code
        if root.char is not None:
            self.codes[root.char] = current_code
            self.reverse_mapping[current_code] = root.char
        # Traverse the left and right children
        self.build_codes_helper(root.left, current_code + "0")
        self.build_codes_helper(root.right, current_code + "1")

    # Generates Huffman codes for all characters
    def build_codes(self, root):
        self.build_codes_helper(root, "")

    # Compresses the input text into a binary string
    def compress(self, text):
        frequency = self.build_frequency_dict(text)
        heap = self.build_heap(frequency)
        root = self.merge_nodes(heap)
        self.build_codes(root)
        # Encode the text
        encoded_text = "".join(self.codes[char] for char in text)
        return encoded_text

    # Decompresses a binary string into the original text
    def decompress(self, encoded_text):
        current_code = ""
        decoded_text = ""
        # Map binary codes back to characters
        for bit in encoded_text:
            current_code += bit
            if current_code in self.reverse_mapping:
                decoded_text += self.reverse_mapping[current_code]
                current_code = ""
        return decoded_text


# Main GUI Application Class
class HuffmanApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Huffman Compression Program")
        self.resize(800, 600)

        self.huffman = HuffmanCoding()  # Instance of HuffmanCoding for operations

        # Widgets for user input and results
        self.text_input = QTextEdit(self)  # Input text area
        self.character_count_label = QLabel("Character Count: 0")  # Character count display
        self.word_count_label = QLabel("Word Count: 0")  # Word count display
        self.compress_button = QPushButton("Compress")  # Button to compress text
        self.file_button = QPushButton("Select File")  # Button to select a file for compression
        self.show_tree_button = QPushButton("Show Huffman Tree")  # Button to display the Huffman Tree
        self.new_compression_button = QPushButton("New Compression")  # Button to start a new compression
        self.compression_ratio_button = QPushButton("Show Compression Ratio")  # Button to show compression ratio

        # Labels to display results
        self.result_label = QLabel("Result: ")
        self.result_label.setWordWrap(True)  # Enable text wrapping for readability

        self.frequency_label = QLabel("Character Frequencies:\n")
        self.frequency_label.setWordWrap(True)

        # Radio buttons for selecting input mode
        self.radio_text = QRadioButton("Text Input")
        self.radio_file = QRadioButton("File Input")
        self.radio_text.setChecked(True)  # Default to text input mode

        # Group the radio buttons
        radio_group = QButtonGroup(self)
        radio_group.addButton(self.radio_text)
        radio_group.addButton(self.radio_file)

        # Scrollable areas for frequency and result displays
        self.frequency_scroll_area = QScrollArea()
        self.frequency_scroll_area.setWidgetResizable(True)
        self.frequency_widget = QWidget()
        self.frequency_layout = QVBoxLayout()
        self.frequency_widget.setLayout(self.frequency_layout)
        self.frequency_layout.addWidget(self.frequency_label)
        self.frequency_scroll_area.setWidget(self.frequency_widget)

        self.result_scroll_area = QScrollArea()
        self.result_scroll_area.setWidgetResizable(True)
        self.result_widget = QWidget()
        self.result_layout = QVBoxLayout()
        self.result_widget.setLayout(self.result_layout)
        self.result_layout.addWidget(self.result_label)
        self.result_scroll_area.setWidget(self.result_widget)

        # Main layout for the application
        layout = QVBoxLayout()
        layout.addWidget(self.radio_text)
        layout.addWidget(self.text_input)
        layout.addWidget(self.character_count_label)
        layout.addWidget(self.word_count_label)
        layout.addWidget(self.radio_file)
        layout.addWidget(self.file_button)
        layout.addWidget(self.compress_button)
        layout.addWidget(self.show_tree_button)
        layout.addWidget(self.new_compression_button)
        layout.addWidget(self.compression_ratio_button)
        layout.addWidget(self.frequency_scroll_area)
        layout.addWidget(self.result_scroll_area)

        # Set the layout for the main window
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Connect buttons and text input to their respective methods
        self.compress_button.clicked.connect(self.handle_compression)
        self.file_button.clicked.connect(self.handle_file_selection)
        self.show_tree_button.clicked.connect(self.show_huffman_tree)
        self.new_compression_button.clicked.connect(self.start_new_compression)
        self.compression_ratio_button.clicked.connect(self.show_compression_ratio)
        self.text_input.textChanged.connect(self.update_counts)

        self.tree_window = None  # Placeholder for the Huffman Tree display window

    # Handles compression when "Compress" button is clicked
    def handle_compression(self):
        if self.radio_text.isChecked():
            text = self.text_input.toPlainText()
            if not text:
                QMessageBox.warning(self, "Warning", "Text input cannot be empty!")
                return
            frequency = self.huffman.build_frequency_dict(text)
            self.display_frequencies(frequency)

            encoded = self.huffman.compress(text)
            decoded = self.huffman.decompress(encoded)
            self.result_label.setText(f"Compressed: {encoded[:50]}...\nDecompressed: {decoded}")
        else:
            QMessageBox.warning(self, "Warning", "Use the file selection button to compress a document!")

    # Allows the user to select a file and compress its content
    def handle_file_selection(self):
        file_filter = "Documents (*.pdf *.odf *.docx)"
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", file_filter)

        if file_path:
            try:
                text = self.read_file_content(file_path)
                frequency = self.huffman.build_frequency_dict(text)
                self.display_frequencies(frequency)

                encoded = self.huffman.compress(text)
                decoded = self.huffman.decompress(encoded)
                self.result_label.setText(f"Compressed: {encoded[:50]}...\nDecompressed: {decoded[:50]}...")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to process file: {str(e)}")

    # Displays the character frequencies in the GUI
    def display_frequencies(self, frequency):
        freq_str = "\n".join(f"'{repr(char)}': {freq}" for char, freq in sorted(frequency.items()))
        self.frequency_label.setText(f"Character Frequencies:\n{freq_str}")

    # Reads content from supported file formats
    def read_file_content(self, file_path):
        import os
        from PyPDF2 import PdfReader
        from docx import Document

        _, ext = os.path.splitext(file_path)
        if ext == ".pdf":
            reader = PdfReader(file_path)
            return " ".join(page.extract_text() for page in reader.pages)
        elif ext == ".docx":
            doc = Document(file_path)
            return "\n".join(para.text for para in doc.paragraphs)
        elif ext == ".odf":
            from odf.opendocument import load
            from odf.text import P

            doc = load(file_path)
            return "\n".join(p.text for p in doc.getElementsByType(P))
        else:
            raise ValueError("Unsupported file type")

    # Displays the Huffman Tree in a separate window
    def show_huffman_tree(self):
        if not self.huffman.root:
            QMessageBox.warning(self, "Warning", "No Huffman tree to display! Compress text first.")
            return

        if not self.tree_window:
            self.tree_window = HuffmanTreeWindow(self.huffman.root)
        self.tree_window.show()

    # Updates the character and word counts as the user types
    def update_counts(self):
        text = self.text_input.toPlainText()
        self.character_count_label.setText(f"Character Count: {len(text)}")
        word_count = len(text.split())
        self.word_count_label.setText(f"Word Count: {word_count}")

    # Resets the application for a new compression
    def start_new_compression(self):
        self.text_input.clear()  # Clear the text input
        self.character_count_label.setText("Character Count: 0")  # Reset character count
        self.word_count_label.setText("Word Count: 0")  # Reset word count
        self.frequency_label.setText("Character Frequencies:\n")  # Clear frequency display
        self.result_label.setText("Result: ")  # Clear result display
        self.huffman = HuffmanCoding()  # Reset HuffmanCoding instance
        if self.tree_window:
            self.tree_window.close()  # Close the Huffman Tree window if open
            self.tree_window = None

    # Calculates and displays the compression ratio
    def show_compression_ratio(self):
        """
        Calculates and displays the compression ratio.
        """
        if not self.huffman.codes:
            QMessageBox.warning(self, "Warning", "No compressed data available! Compress text first.")
            return

        # Get the original text
        if self.radio_text.isChecked():
            text = self.text_input.toPlainText()
        else:
            QMessageBox.warning(self, "Warning", "Compression ratio is only available for text input.")
            return

        if not text:
            QMessageBox.warning(self, "Warning", "Text input is empty!")
            return

        # Calculate the size of the original text in bits (assuming 8 bits per character)
        original_size = len(text) * 8

        # Calculate the size of the compressed data in bits
        compressed_text = self.huffman.compress(text)
        compressed_size = len(compressed_text)  # Each '0' or '1' is 1 bit

        # Calculate the compression ratio
        compression_ratio = compressed_size / original_size

        # Display the result in a message box
        QMessageBox.information(
            self,
            "Compression Ratio",
            f"Original Size: {original_size} bits\n"
            f"Compressed Size: {compressed_size} bits\n"
            f"Compression Ratio: {compression_ratio:.2f}"
        )


# Window for visualizing the Huffman Tree
class HuffmanTreeWindow(QWidget):
    def __init__(self, root):
        super().__init__()
        self.setWindowTitle("Huffman Tree")
        self.resize(800, 600)

        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        layout = QVBoxLayout()
        layout.addWidget(self.view)
        self.setLayout(layout)

        self.draw_tree(root, QPointF(400, 50), 200)

    # Recursively draws the Huffman Tree
    def draw_tree(self, node, pos, x_offset):
        if node is None:
            return

        circle_radius = 20
        ellipse = QGraphicsEllipseItem(pos.x() - circle_radius, pos.y() - circle_radius, 2 * circle_radius, 2 * circle_radius)
        ellipse.setBrush(Qt.GlobalColor.lightGray)
        self.scene.addItem(ellipse)

        label = repr(node.char) if node.char else '␀'  # Show character or null for merged nodes
        text = QGraphicsTextItem(f"{label}\n{node.freq}")
        text.setPos(pos.x() - 15, pos.y() - 15)
        self.scene.addItem(text)

        # Draw left child
        if node.left:
            left_pos = QPointF(pos.x() - x_offset, pos.y() + 80)
            self.scene.addLine(pos.x(), pos.y() + circle_radius, left_pos.x(), left_pos.y() - circle_radius)
            self.draw_tree(node.left, left_pos, x_offset / 1.5)

        # Draw right child
        if node.right:
            right_pos = QPointF(pos.x() + x_offset, pos.y() + 80)
            self.scene.addLine(pos.x(), pos.y() + circle_radius, right_pos.x(), right_pos.y() - circle_radius)
            self.draw_tree(node.right, right_pos, x_offset / 1.5)


# Entry point for the application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HuffmanApp()
    window.show()
    sys.exit(app.exec())