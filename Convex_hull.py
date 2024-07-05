import numpy as np
import matplotlib.pyplot as plt
from tkinter import Tk, Label, Entry, Button, Frame, Canvas, Scrollbar, messagebox


class PayoffMatrixInput:
    def __init__(self, root):
        self.root = root
        self.root.title("Input Payoff Matrices")

        self.player1_label = Label(
            root, text="Number of strategies for Player 1:")
        self.player1_label.grid(row=0, column=0)
        self.player1_entry = Entry(root)
        self.player1_entry.grid(row=0, column=1)

        self.player2_label = Label(
            root, text="Number of strategies for Player 2:")
        self.player2_label.grid(row=1, column=0)
        self.player2_entry = Entry(root)
        self.player2_entry.grid(row=1, column=1)

        self.submit_button = Button(
            root, text="Submit", command=self.create_matrix_input)
        self.submit_button.grid(row=2, columnspan=2)

    def create_matrix_input(self):
        try:
            self.num_strategies_player1 = int(self.player1_entry.get())
            self.num_strategies_player2 = int(self.player2_entry.get())
        except ValueError:
            messagebox.showerror(
                "Input Error", "Please enter valid numbers for strategies.")
            return

        # Clear previous matrix-related widgets
        for widget in self.root.grid_slaves():
            if int(widget.grid_info()["row"]) > 2:
                widget.grid_forget()

        self.payoff_entries = []

        self.matrix_label = Label(
            self.root, text="Enter payoff pairs (Player 1, Player 2):")
        self.matrix_label.grid(row=3, column=0, columnspan=3)

        # Create a canvas and scrollbars
        self.canvas = Canvas(self.root)
        self.canvas.grid(row=4, column=0, columnspan=2)

        self.v_scrollbar = Scrollbar(
            self.root, orient="vertical", command=self.canvas.yview)
        self.v_scrollbar.grid(row=4, column=2, sticky='ns')
        self.h_scrollbar = Scrollbar(
            self.root, orient="horizontal", command=self.canvas.xview)
        self.h_scrollbar.grid(row=5, column=0, columnspan=2, sticky='ew')

        self.canvas.configure(
            yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)

        self.matrix_frame = Frame(self.canvas)
        self.canvas.create_window(
            (0, 0), window=self.matrix_frame, anchor='nw')

        self.entry_frames = []
        for i in range(self.num_strategies_player1):
            row_entries = []
            row_frame = Frame(self.matrix_frame)
            row_frame.grid(row=i, column=0)
            for j in range(self.num_strategies_player2):
                entry_frame = Frame(row_frame)
                entry_frame.grid(row=0, column=j)

                Label(entry_frame, text="(").pack(side="left")
                entry1 = Entry(entry_frame, width=5)
                entry1.pack(side="left")
                Label(entry_frame, text=",").pack(side="left")
                entry2 = Entry(entry_frame, width=5)
                entry2.pack(side="left")
                Label(entry_frame, text=")").pack(side="left")

                row_entries.append((entry1, entry2))
            self.payoff_entries.append(row_entries)
            self.entry_frames.append(row_frame)

        self.calculate_button = Button(
            self.root, text="Calculate", command=self.calculate_results)
        self.calculate_button.grid(
            row=6 + self.num_strategies_player1, columnspan=2)

        self.matrix_frame.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def calculate_results(self):
        player1_payoffs, player2_payoffs = self.extract_payoff_matrices()
        if player1_payoffs is None or player2_payoffs is None:
            return

        payoff_vectors = self.compute_payoff_vectors(
            player1_payoffs, player2_payoffs)
        hull_indices = self.gift_wrapping(payoff_vectors)
        hull_points = payoff_vectors[hull_indices]

        pareto_points = self.find_pareto_optimal_points(payoff_vectors)

        self.plot_results(payoff_vectors, hull_points, pareto_points)

    def extract_payoff_matrices(self):
        try:
            player1_payoffs = np.zeros(
                (self.num_strategies_player1, self.num_strategies_player2), dtype=int)
            player2_payoffs = np.zeros(
                (self.num_strategies_player1, self.num_strategies_player2), dtype=int)
            for i, row in enumerate(self.payoff_entries):
                for j, (entry1, entry2) in enumerate(row):
                    player1_payoffs[i, j] = int(entry1.get())
                    player2_payoffs[i, j] = int(entry2.get())
            return player1_payoffs, player2_payoffs
        except ValueError:
            messagebox.showerror(
                "Input Error", "Please enter valid numbers for the payoff matrices.")
            return None, None

    def compute_payoff_vectors(self, player1_payoffs, player2_payoffs):
        payoff_vectors = []
        for i in range(self.num_strategies_player1):
            for j in range(self.num_strategies_player2):
                payoff_vectors.append(
                    [player1_payoffs[i, j], player2_payoffs[i, j]])
        return np.array(payoff_vectors)

    def find_pareto_optimal_points(self, payoff_vectors):
        pareto_points = []
        for i, payoff1 in enumerate(payoff_vectors):
            pareto = True
            for j, payoff2 in enumerate(payoff_vectors):
                if i != j and all(payoff2 >= payoff1) and any(payoff2 > payoff1):
                    pareto = False
                    break
            if pareto:
                pareto_points.append(payoff1)
        return np.array(pareto_points)

    def gift_wrapping(self, points):
        hull = []
        n = len(points)
        point_on_hull = np.argmin(points[:, 0])

        while True:
            hull.append(point_on_hull)
            end_point = (point_on_hull + 1) % n

            for j in range(n):
                if j != hull[-1]:
                    # Compute the 2D cross product manually
                    direction = np.array(
                        [points[end_point] - points[hull[-1]], points[j] - points[hull[-1]]])
                    cross_product = direction[0, 0] * direction[1,
                                                                1] - direction[0, 1] * direction[1, 0]
                    if cross_product < 0:
                        end_point = j

            point_on_hull = end_point
            if end_point == hull[0]:
                break

        return np.array(hull)

    # Plot the convex hull and fill the inside
    def plot_results(self, payoff_vectors, hull_points, pareto_points):
        plt.figure(figsize=(10, 6))
        plt.plot(payoff_vectors[:, 0], payoff_vectors[:,
                 1], 'o', label='Payoff Points')
        plt.plot(hull_points[:, 0], hull_points[:, 1],
                 'k-', label='Convex Hull')
        plt.plot(np.append(hull_points[:, 0], hull_points[0, 0]), np.append(
            hull_points[:, 1], hull_points[0, 1]), 'k-')

        pareto_points = np.array(
            sorted(pareto_points, key=lambda point: point[0]))
        pareto_points = np.array(
            sorted(pareto_points, key=lambda point: point[1], reverse=True))

        plt.plot(pareto_points[:, 0], pareto_points[:, 1],
                 'o:r', label='Pareto Optimal Points')
        plt.fill(hull_points[:, 0], hull_points[:, 1], 'gray', alpha=0.2)

        plt.xlabel('Player 1 Payoff')
        plt.ylabel('Player 2 Payoff')
        plt.title(
            'Convex Hull of Feasible Payoff Vectors and Pareto Optimal Points')
        plt.legend()
        plt.grid(True)
        plt.show()


if __name__ == "__main__":
    root = Tk()
    app = PayoffMatrixInput(root)
    root.mainloop()
