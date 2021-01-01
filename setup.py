from distutils.core import setup

pack_version = __import__('rpy2_R6').__version__

if __name__ == '__main__':
    setup(
        name='rpy2-R6',
        version=pack_version,
        description='Mapping the R package R6',
        license='MIT',
        requires=['rpy2(>=3.4)'],
        packages=['rpy2_R6'],
        classifiers=['Programming Language :: Python',
                     'Programming Language :: Python :: 3',
                     'Programming Language :: Python :: 3.6',
                     'Programming Language :: Python :: 3.7',
                     'Programming Language :: Python :: 3.8',
                     ('License :: OSI Approved :: GNU General '
                      'MIT'),
                     'Intended Audience :: Developers',
                     'Intended Audience :: Science/Research',
                     'Development Status :: 3 - Alpha']
    )
