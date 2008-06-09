%define build_asterisk 0
%{?_with_asterisk: %{expand: %%global build_asterisk 1}}
%{?_without_asterisk: %{expand: %%global build_asterisk 0}}

%define	major _0
%define libname	%mklibname q931 %{major}

Summary:	Versatile ISDN framework for Linux
Name:		visdn
Version:	0.18.2
Release:	%mkrel 5
License:	GPL
Group:		System/Libraries
URL:		http://www.visdn.org/
Source0:	http://www.visdn.org/download/visdn-%{version}.tar.bz2
Patch0:		visdn-0.16.1-udev_090.diff
Patch1:		visdn-0.16.1-sms_spooler_dir.diff
Patch2:		visdn-0.18.2-2617_fixes.diff
Patch10:	visdn-0.16.1-dkms_friendly.diff
BuildRequires:	libtool
BuildRequires:	autoconf2.5
BuildRequires:	automake1.8
BuildRequires:	ppp-devel
%if %{build_asterisk}
BuildRequires:	asterisk
BuildRequires:	asterisk-devel
%endif
BuildRequires:	zlib-devel
BuildRoot:	%{_tmppath}/%{name}-%{version}-build

%description
vISDN is an ISDN framework designed to be clean, general purpose,
standards compliant, for voice and data applications.

%package -n	%{libname}
Summary:	Versatile ISDN framework for Linux (shared libraries)
Group:          System/Libraries

%description -n	%{libname}
vISDN is an ISDN framework designed to be clean, general purpose,
standards compliant, for voice and data applications.

This package provides the shared libraries for %{name}.

%package -n	%{libname}-devel
Summary:	Header files and libraries needed for development with %{name}
Group:		Development/C
Provides:	%{name}-devel = %{version}
Provides:	lib%{name}-devel = %{version}
Provides:	libq931-devel = %{version}
Requires:	%{libname} = %{version}

%description -n	%{libname}-devel
vISDN is an ISDN framework designed to be clean, general purpose,
standards compliant, for voice and data applications.

This package includes the header files and libraries needed for
developing programs using %{name}.

%package -n	ppp-%{name}
Summary:	Cologne Chip's HFC-4S and HFC-8S vISDN driver for pppd
Group:		System/Servers
Requires:	ppp

%description -n	ppp-%{name}
Cologne Chip's HFC-4S and HFC-8S vISDN driver for pppd.

%package -n	asterisk-%{name}
Summary:	Cologne Chip's HFC-4S and HFC-8S vISDN driver for the Asterisk PBX
Group:		System/Servers
Requires:	asterisk
Requires:	dkms-%{name} = %{version}

%description -n	asterisk-%{name}
Cologne Chip's HFC-4S and HFC-8S vISDN driver for the Asterisk PBX.

%package -n	dkms-%{name}
Summary:	Versatile ISDN framework kernel drivers
Group:		System/Kernel and hardware
Requires:	dkms
Requires:	%{name}-tools = %{version}
Requires:	autoconf2.5
Requires:	automake1.8
Requires:	udev >= 090

%description -n	dkms-%{name}
vISDN is an ISDN framework designed to be clean, general purpose,
standards compliant, for voice and data applications.

This package contains the kernel drivers.

%package	tools
Summary:	Various tools for %{name}
Group:          System/Kernel and hardware

%description	tools
vISDN is an ISDN framework designed to be clean, general purpose,
standards compliant, for voice and data applications.

Various tools for %{name}

%prep

%setup -q -n %{name}-%{version}

%patch0 -p0
%patch1 -p0
%patch2 -p1

# tuck away the needed source for the dkms package
mkdir -p dkms
pushd dkms
cp -rp ../config ../modules .
cp -p ../Makefile.am ../aclocal.m4 ../configure.ac ../config.h.in ../COPYING ../ChangeLog ../AUTHORS  .
%patch10 -p0
export WANT_AUTOCONF_2_5=1
touch INSTALL NEWS README
# lib64 fix
perl -pi -e "s|/usr/lib|%{_libdir}|g" configure*
libtoolize --copy --force; aclocal -I config; autoconf; automake --gnu --add-missing --copy
rm -rf autom4te.cache
popd


# lib64 fix
perl -pi -e "s|/usr/lib|%{_libdir}|g" configure*

export WANT_AUTOCONF_2_5=1
rm -f configure
libtoolize --copy --force; aclocal -I config; autoconf; automake --gnu --add-missing --copy

%build

%configure2_5x \
    --enable-shared \
    --enable-static \
    --disable-kernel-modules \
%if %{build_asterisk}
    --enable-asterisk-modules \
    --with-asterisk-modules=%{_libdir}/asterisk \
    --with-asterisk-config=%{_sysconfdir}/asterisk \
%else
    --disable-asterisk-modules \
%endif
    --enable-pppd-plugin

%make

%install
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%makeinstall_std

install -d %{buildroot}%{_sysconfdir}/visdn

%if %{build_asterisk}
install -d %{buildroot}%{_sysconfdir}/asterisk
install -d %{buildroot}%{_localstatedir}/lib/asterisk/sms_spooler
install -m0644 samples/vgsm.conf %{buildroot}%{_sysconfdir}/asterisk/vgsm.conf
install -m0644 samples/vgsm_operators.conf %{buildroot}%{_sysconfdir}/asterisk/vgsm_operators.conf
install -m0644 samples/visdn.conf.sample %{buildroot}%{_sysconfdir}/asterisk/visdn.conf
%endif

install -d %{buildroot}/usr/src/%{name}-%{version}-%{release}/
cp -rp dkms/* %{buildroot}/usr/src/%{name}-%{version}-%{release}/

install -d %{buildroot}/etc/udev/rules.d
install -m0644 samples/30-visdn.rules %{buildroot}/etc/udev/rules.d/30-visdn.rules

cat > %{buildroot}/usr/src/%{name}-%{version}-%{release}/dkms.conf <<EOF
PACKAGE_VERSION="%{version}-%{release}"

# Items below here should not have to change with each driver version
PACKAGE_NAME="%{name}"

MAKE[0]="./configure --prefix=%{_prefix} --sysconfdir=%{_sysconfdir} --libdir=%{_libdir} --enable-drivers=hfc-usb,hfc-pci,hfc-4s,hfc-e1; make"
CLEAN="make clean"

BUILT_MODULE_NAME[0]="kfifo"
BUILT_MODULE_NAME[1]="lapd"
BUILT_MODULE_NAME[2]="visdn-core"
BUILT_MODULE_NAME[3]="visdn-ec"
BUILT_MODULE_NAME[4]="visdn-hfc-4s"
BUILT_MODULE_NAME[5]="visdn-hfc-e1"
BUILT_MODULE_NAME[6]="visdn-hfc-pci"
BUILT_MODULE_NAME[7]="visdn-hfc-usb"
BUILT_MODULE_NAME[8]="visdn-netdev"
BUILT_MODULE_NAME[9]="visdn-ppp"
BUILT_MODULE_NAME[10]="visdn-softcxc"
BUILT_MODULE_NAME[11]="visdn-streamport"
BUILT_MODULE_NAME[12]="visdn-timer-system"
BUILT_MODULE_NAME[13]="visdn-vgsm"

BUILT_MODULE_LOCATION[0]="modules/kfifo"
BUILT_MODULE_LOCATION[1]="modules/lapd"
BUILT_MODULE_LOCATION[2]="modules/core"
BUILT_MODULE_LOCATION[3]="modules/ec"
BUILT_MODULE_LOCATION[4]="modules/hfc-4s"
BUILT_MODULE_LOCATION[5]="modules/hfc-e1"
BUILT_MODULE_LOCATION[6]="modules/hfc-pci"
BUILT_MODULE_LOCATION[7]="modules/hfc-usb"
BUILT_MODULE_LOCATION[8]="modules/netdev"
BUILT_MODULE_LOCATION[9]="modules/ppp"
BUILT_MODULE_LOCATION[10]="modules/softcxc"
BUILT_MODULE_LOCATION[11]="modules/streamport"
BUILT_MODULE_LOCATION[12]="modules/timer-system"
BUILT_MODULE_LOCATION[13]="modules/vgsm"

DEST_MODULE_LOCATION[0]="/kernel/drivers/isdn/visdn"
DEST_MODULE_LOCATION[1]="/kernel/drivers/isdn/visdn"
DEST_MODULE_LOCATION[2]="/kernel/drivers/isdn/visdn"
DEST_MODULE_LOCATION[3]="/kernel/drivers/isdn/visdn"
DEST_MODULE_LOCATION[4]="/kernel/drivers/isdn/visdn"
DEST_MODULE_LOCATION[5]="/kernel/drivers/isdn/visdn"
DEST_MODULE_LOCATION[6]="/kernel/drivers/isdn/visdn"
DEST_MODULE_LOCATION[7]="/kernel/drivers/isdn/visdn"
DEST_MODULE_LOCATION[8]="/kernel/drivers/isdn/visdn"
DEST_MODULE_LOCATION[9]="/kernel/drivers/isdn/visdn"
DEST_MODULE_LOCATION[10]="/kernel/drivers/isdn/visdn"
DEST_MODULE_LOCATION[11]="/kernel/drivers/isdn/visdn"
DEST_MODULE_LOCATION[12]="/kernel/drivers/isdn/visdn"
DEST_MODULE_LOCATION[13]="/kernel/drivers/isdn/visdn"

AUTOINSTALL=yes
EOF
						      
# cleanup
rm -rf %{buildroot}%{_libdir}/pppd/*/*.a
rm -rf %{buildroot}%{_libdir}/pppd/*/*.la
rm -rf %{buildroot}%{_libdir}/asterisk/*.a
rm -rf %{buildroot}%{_libdir}/asterisk/*.la
rm -rf docs/doxy/.arch-*

%if %mdkversion < 200900
%post -n %{libname} -p /sbin/ldconfig
%endif

%if %mdkversion < 200900
%postun -n %{libname} -p /sbin/ldconfig
%endif

%post -n dkms-%{name}
dkms add -m	%{name} -v %{version}-%{release} --rpm_safe_upgrade
dkms build -m	%{name} -v %{version}-%{release} --rpm_safe_upgrade
dkms install -m	%{name} -v %{version}-%{release} --rpm_safe_upgrade

%preun -n dkms-%{name}
dkms remove -m	%{name} -v %{version}-%{release} --rpm_safe_upgrade --all

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%files -n %{libname}
%defattr(-,root,root)
%doc AUTHORS COPYING ChangeLog README TODO docs/* samples/ethereal_coloring_rules
%{_libdir}/*.so.*

%files -n %{libname}-devel
%defattr(-,root,root)
%dir %{_includedir}/libq931
%{_includedir}/libq931/*.h
%{_libdir}/*.so
%{_libdir}/*.a
%{_libdir}/*.la

%files -n ppp-%{name}
%defattr(-,root,root)
%doc samples/ppp_dialout
%{_libdir}/pppd/*/*.so

%if %{build_asterisk}
%files -n asterisk-%{name}
%defattr(-,root,root)
%doc samples/extensions.conf.sample
%doc samples/extensions.conf.sample_passthru
%doc samples/vgsm.conf
%doc samples/vgsm_operators.conf
%doc samples/visdn.conf.sample
%doc samples/visdn.conf.sample_passthru
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/asterisk/visdn.conf
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/asterisk/vgsm.conf
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/asterisk/vgsm_operators.conf
%attr(0755,root,root) %{_libdir}/asterisk/app_visdn_ppp.so
%attr(0755,root,root) %{_libdir}/asterisk/chan_vgsm.so
%attr(0755,root,root) %{_libdir}/asterisk/chan_visdn.so
%attr(0755,asterisk,asterisk) %dir %{_localstatedir}/lib/asterisk/sms_spooler
%endif

%files -n dkms-%{name}
%defattr(-,root,root)
%doc samples/device-pci-0000:00:06.0
%doc samples/device-pci-0000:00:07.0
%doc samples/device-pci-0000:00:09.0
%doc samples/device-usb-2-2
%doc vgsm_firmware/firmware-*img vgsm_firmware/README
%dir %{_sysconfdir}/visdn
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/udev/rules.d/30-visdn.rules
#%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/zaptel.conf
/usr/src/%{name}-%{version}-%{release}

%files tools
%defattr(-,root,root)
%attr(0755,root,root) %{_sbindir}/vgsmctl
%attr(0755,root,root) %{_sbindir}/visdn_configurator
%attr(0755,root,root) %{_sbindir}/visdnctl


