import numpy as np
import matplotlib
print(matplotlib.matplotlib_fname())
import matplotlib.pyplot as plt


print("Hello, World!")
plt.plot([0,1])
plt.title("line")
plt.xlabel("x")
plt.ylabel("y")
plt.savefig("test_plot.pdf")
